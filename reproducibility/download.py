"""Download and verify a fixed HF release. Default downloads six core files.

Use --all for all published CSV, PNG, metadata and profile files (~2.6GB).
No Hugging Face account, API token, model service or GPU is required.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request

HERE=Path(__file__).resolve().parent


def get_tree(repo,revision):
    url=f'https://huggingface.co/api/datasets/{repo}/tree/{revision}?recursive=true&limit=1000'
    rows=[]
    while url:
        with urllib.request.urlopen(url,timeout=60) as response:
            rows.extend(json.load(response))
            match=re.search(r'<([^>]+)>; rel="next"',response.headers.get('Link',''))
            url=match.group(1) if match else None
    return [r for r in rows if r['type']=='file']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=HERE.parent/'Data/benchmark_tb')
    p.add_argument('--all',action='store_true')
    p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    release=json.loads((HERE/'release_manifest.json').read_text(encoding='utf-8'))
    repo,revision=release['dataset_repository'],release['dataset_revision']
    core={'LongTS_Industrial/test.jsonl','LongTS_Industrial/benchmark_stats.json','synthetic_qa_llm.jsonl','generation_manifest.json','README.md','.gitattributes'}
    files=[r for r in get_tree(repo,revision) if args.all or r['path'] in core]
    def fetch(info):
        path=info['path']
        if Path(path).is_absolute() or '..' in Path(path).parts:raise ValueError('Unsafe remote path')
        target=args.output/path
        target.parent.mkdir(parents=True,exist_ok=True)
        def valid():
            if not target.is_file():return False
            data=target.read_bytes()
            if info.get('lfs'):actual=hashlib.sha256(data).hexdigest();expected=info['lfs']['oid']
            else:actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();expected=info['oid']
            return actual==expected
        if valid():return path
        temporary=target.with_suffix(target.suffix+'.part')
        url=f'https://huggingface.co/datasets/{repo}/resolve/{revision}/'+urllib.parse.quote(path,safe='/')
        with urllib.request.urlopen(url,timeout=120) as response,temporary.open('wb') as out:
            while True:
                block=response.read(1024*1024)
                if not block:break
                out.write(block)
        temporary.replace(target)
        if not valid():raise ValueError('Remote object digest mismatch: '+path)
        return path
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i,path in enumerate(pool.map(fetch,files),1):
            if i<=6 or i%100==0:print(f'{i}/{len(files)} verified: {path}',flush=True)
    print('Completed pinned dataset:',revision)


if __name__=='__main__':main()
