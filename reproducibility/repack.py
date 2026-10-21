"""Reproduce the final published test using its original Windows conventions.

Only repacks released QA records; does not synthesize data or call an LLM.
Output must be a new file. No existing split is removed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import ntpath
import random


def repack(source,output):
    with source.open(encoding='utf-8-sig') as f:
        rows=[json.loads(line) for line in f if line.strip()]
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate sample IDs: refusing ambiguous packing.')
    random.Random(42).shuffle(rows)
    for r in rows:
        if 'timeseries_path' in r and not r['timeseries_path'].startswith('..'):
            r['timeseries_path']=ntpath.join('..',r['timeseries_path'])
    data=''.join(json.dumps(r,ensure_ascii=False)+'\r\n' for r in rows).encode('utf-8')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as f:f.write(data)
    return {'records':len(rows),'qa_pairs':sum(len(r['qa_pairs']) for r in rows),
            'sha256':hashlib.sha256(data).hexdigest(),'output':str(output)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(repack(args.source,args.output),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
