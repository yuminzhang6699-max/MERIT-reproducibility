"""Verify the frozen benchmark without model inference or non-stdlib packages."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent


def read_jsonl(path):
    with path.open(encoding='utf-8-sig') as f:
        return [json.loads(line) for line in f if line.strip()]


def inspect(test_path, data_dir=None, check_assets=False):
    release = json.loads((HERE/'release_manifest.json').read_text(encoding='utf-8'))
    data = test_path.read_bytes()
    records = read_jsonl(test_path)
    canonical = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    ids = [r['id'] for r in records]
    keys, problems, missing = set(), [], []
    for r in records:
        n = r['metadata']['total_length']
        length = n-1
        ratio = r['metadata']['needle_ratio']
        expected = 'easy' if length <= 1000 else ('medium' if ratio > .05 else 'hard') if length <= 3000 else ('hard' if ratio > .03 else 'expert') if length <= 5000 else 'expert'
        if r['metadata']['difficulty'] != expected:
            problems.append({'id':r['id'],'error':'difficulty_mismatch'})
        for event in r['ground_truth_events']:
            start,end=event['range']
            if not 0 <= start < end <= n:
                problems.append({'id':r['id'],'error':'invalid_half_open_event_range'})
        for q in r['qa_pairs']:
            key = (r['id'],q['level'],q['question'])
            if key in keys:problems.append({'id':r['id'],'error':'duplicate_qa_key'})
            keys.add(key)
            if q['level'] not in ['L1','L2','L3','L4'] or not isinstance(q['answer'],str):
                problems.append({'id':r['id'],'error':'invalid_qa'})
        if check_assets:
            if data_dir is None:raise ValueError('--assets requires --data-dir')
            path=r['timeseries_path'].replace('\\','/')
            while path.startswith('../'):path=path[3:]
            stem=path[:-4]
            for asset in [path,stem+'_eval.png',stem+'_metadata.json',stem+'_data_profile.json']:
                if not (data_dir/asset).is_file():missing.append(asset)
    n_qa=sum(len(r['qa_pairs']) for r in records)
    canonical_match=hashlib.sha256(canonical).hexdigest()==release['canonical_records_sha256']
    byte_match=hashlib.sha256(data).hexdigest()==release['test_sha256']
    return {'test':str(test_path),'dataset_revision':release['dataset_revision'],
        'n_samples':len(records),'n_unique_sample_ids':len(set(ids)),'n_qa':n_qa,
        'byte_sha256_match':byte_match,'canonical_record_sequence_match':canonical_match,
        'by_domain':dict(Counter(r['domain'] for r in records)),
        'by_level':dict(Counter(q['level'] for r in records for q in r['qa_pairs'])),
        'by_difficulty':dict(Counter(r['metadata']['difficulty'] for r in records)),
        'by_n_samples':dict(Counter(r['metadata']['total_length'] for r in records)),
        'problems':problems,'asset_check':'existence_only' if check_assets else 'not_requested',
        'missing_assets':missing,
        'passed':canonical_match and len(records)==release['n_samples'] and len(set(ids))==len(records) and n_qa==release['n_qa'] and not problems and not missing,
        'scope':'release data identity and structure'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,default=HERE.parent/'Data/benchmark_tb')
    p.add_argument('--test',type=Path)
    p.add_argument('--assets',action='store_true')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    report=inspect(args.test or args.data_dir/'LongTS_Industrial/test.jsonl',args.data_dir,args.assets)
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text+'\n',encoding='utf-8')
    print(text)
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
