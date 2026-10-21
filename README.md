# MERIT reproducibility supplement

This repository packages the already public MERIT / LongTS-Industrial implementation with a versioned reproducibility guide, metadata specification, exact prompts, split/difficulty clarification, and verification tools.

**Original implementation:** [ctacyk/MERIT](https://github.com/ctacyk/MERIT), pinned source commit `a0a4d3dbf8022222387c5ee421626ba0d7836633`.

**Original dataset:** [ANTICH/LongTS-Industrial](https://huggingface.co/datasets/ANTICH/LongTS-Industrial), pinned revision `833586d18a6a207464944dc41de6dba007f3b862`.

The code copyright and MIT license of CHEN TINGAN are preserved. TimeBlender retains its separate attribution and MIT notice. This supplement does not claim authorship of the original benchmark code and does not replace the original dataset.

## Start here

- [Reproducibility guide](reproducibility/README.md)
- [Generation pipeline](reproducibility/GENERATION.md)
- [Metadata specification](reproducibility/METADATA.md) and [machine-readable schema](reproducibility/metadata.schema.json)
- [Full model, QA-generation and judge prompts](reproducibility/PROMPTS.md)
- [Actual unified test split and difficulty definitions](reproducibility/SPLITS_AND_DIFFICULTY.md)
- [Evaluation settings](reproducibility/EVALUATION.md)

## No-GPU reproduction check

```bash
python reproducibility/download.py --output Data/benchmark_tb
python reproducibility/verify.py --data-dir Data/benchmark_tb
python reproducibility/repack.py --source Data/benchmark_tb/synthetic_qa_llm.jsonl --output reproduced/test.jsonl
python reproducibility/verify.py --test reproduced/test.jsonl
```

The helpers use the Python standard library to download the fixed public files, verify dataset structure and reproduce final packing. See the guide for all-assets download and API-dependent generation/evaluation stages.

## Clarifications

The release has one test split: 1716 series and 8412 QA. The generator interval count L is 1000/3000/5000/10000; inclusion of both timestamp endpoints produces T=L+1 observations. Difficulty uses L while the saved total_length stores T. Event ranges follow zero-based [start,end).

The released source QA reproduces the published test byte-for-byte with the documented seed, path conventions and newline format.

Original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md) and [UPSTREAM_README.zh-CN.md](UPSTREAM_README.zh-CN.md). New reproducibility materials do not change the original release's inputs, references or results.
