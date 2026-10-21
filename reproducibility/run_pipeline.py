"""Explicit generation-stage entry points for the existing public code.

Requires the original scientific/API dependencies for generation. --plan uses
only the standard library and never calls models or creates generated data.
"""
from pathlib import Path
import argparse
import importlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['synthesize','profile','qa','pack','all'],required=True)
    p.add_argument('--data-dir',type=Path,required=True,help='Use a new directory, not the frozen downloaded release.')
    p.add_argument('--plan',action='store_true')
    args=p.parse_args()
    stages=['synthesize','profile','qa','pack'] if args.stage=='all' else [args.stage]
    data=args.data_dir.resolve()
    if args.plan:
        print(json.dumps({'stages':stages,'new_data_dir':str(data),
            'source_modules':{'synthesize':'MultiAgentTS.scenarios.batch_runner_tb.run_batch',
                'profile':'compute_data_profiles.compute_profile',
                'qa':'MultiAgentTS.scenarios.qa_llm_generator.batch_generate_qa_llm',
                'pack':'reproducibility.repack (published Windows packing conventions)'},
            'qa_model':'qwen3-max','requires_key_for_qa':True,
            'note':'New QA generation is stochastic and is not a byte-identical re-creation of the released references.'},indent=2))
        return
    if 'qa' in stages and not os.environ.get('DASHSCOPE_API_KEY'):
        raise SystemExit('DASHSCOPE_API_KEY required for the requested QA stage; no generation has started.')
    sys.path.insert(0,str(ROOT))
    data.mkdir(parents=True,exist_ok=True)
    for stage in stages:
        if stage=='synthesize':
            if any(data.glob('**/*.csv')):
                raise SystemExit('Existing CSV files found; choose an empty generation directory.')
            module=importlib.import_module('MultiAgentTS.scenarios.batch_runner_tb')
            module.run_batch(output_base=str(data),lengths=[1000,3000,5000,10000],seeds=[42,123,789],generate_eval_plots=True,skip_existing=False)
        elif stage=='profile':
            module=importlib.import_module('compute_data_profiles')
            for csv in sorted(data.glob('**/*.csv')):
                meta=csv.with_name(csv.stem+'_metadata.json')
                if not meta.is_file():raise ValueError('Missing metadata: '+str(meta))
                profile=module.compute_profile(str(csv),str(meta))
                csv.with_name(csv.stem+'_data_profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
        elif stage=='qa':
            if not list(data.glob('**/*_data_profile.json')):raise SystemExit('Create data profiles before QA generation.')
            if (data/'synthetic_qa_llm.jsonl').exists():raise SystemExit('QA file exists; refusing to append a new generation to old records.')
            module=importlib.import_module('MultiAgentTS.scenarios.qa_llm_generator')
            module.batch_generate_qa_llm(metadata_dir=str(data),output_path=str(data/'synthetic_qa_llm.jsonl'),
                api_key=os.environ['DASHSCOPE_API_KEY'],model='qwen3-max',rpm_limit=10,skip_existing=False)
        elif stage=='pack':
            subprocess.run([sys.executable,str(ROOT/'reproducibility/repack.py'),'--source',str(data/'synthetic_qa_llm.jsonl'),
                '--output',str(data/'LongTS_Industrial/test.jsonl')],check=True)


if __name__=='__main__':main()
