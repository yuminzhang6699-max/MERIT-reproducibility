# Reproducing the released MERIT / LongTS-Industrial benchmark

This guide identifies the **existing released benchmark**, its generation entry points, metadata, exact evaluation prompts, and actual split policy. The helpers added here document and check the release without changing the published CSVs, images, QA references, difficulty labels, or result tables.

## Fixed versions

| Artifact | Immutable identity |
| --- | --- |
| Original generation/evaluation code | [`a0a4d3dbf8022222387c5ee421626ba0d7836633`](https://github.com/ctacyk/MERIT/tree/a0a4d3dbf8022222387c5ee421626ba0d7836633) |
| Dataset | [`833586d18a6a207464944dc41de6dba007f3b862`](https://huggingface.co/datasets/ANTICH/LongTS-Industrial/tree/833586d18a6a207464944dc41de6dba007f3b862) |
| Test file | `LongTS_Industrial/test.jsonl` |
| Test SHA-256 | `2fc190c0b6b9fae57a22bff39493d0c69cebc59dae8a1abf227a7939dc5b3cdd` |
| Scale | 1,716 multichannel series; 8,412 QA pairs; four equipment domains |
| Split policy | One unified test split; no train/validation split in this release |

The original final packer calls its output “v3” in a comment. Use the immutable identities above rather than relying on that internal label. [release_manifest.json](release_manifest.json) is machine-readable.

## Where each reproducibility component is documented

| Component | Documentation | Existing implementation |
| --- | --- | --- |
| Generation and packaging | [GENERATION.md](GENERATION.md) | batch runner → profiles → QA generator → final packer |
| Metadata and interval conventions | [METADATA.md](METADATA.md), [metadata.schema.json](metadata.schema.json) | `ChannelInfo`, `EventMetadata`, `GenerationMetadata` in `scenarios/base.py` |
| Model/QA/judge prompts | [PROMPTS.md](PROMPTS.md) | exact public prompt functions extracted without paraphrasing |
| Evaluation protocol | [EVALUATION.md](EVALUATION.md) | `run_benchmark_eval.py`, `benchmark_eval.py` |
| Split and difficulty definitions | [SPLITS_AND_DIFFICULTY.md](SPLITS_AND_DIFFICULTY.md) | final `pack_final_benchmark.py`, original `compute_difficulty` |

## Check the fixed release without a GPU or API account

Run from the repository root with Python 3.10 or newer:

```bash
# Download test, source QA and generation manifest at the fixed dataset revision.
python reproducibility/download.py --output Data/benchmark_tb

# Verify dataset identity, sample/QA counts, labels and interval structure.
python reproducibility/verify.py --data-dir Data/benchmark_tb

# Reconstruct a new test file from the already published source QA.
# Output must not exist; the helper never removes or overwrites a split.
python reproducibility/repack.py \
  --source Data/benchmark_tb/synthetic_qa_llm.jsonl \
  --output reproduced/LongTS_Industrial/test.jsonl
python reproducibility/verify.py --test reproduced/LongTS_Industrial/test.jsonl
```

The checks above use only the Python standard library and verify dataset structure, labels and deterministic packaging.

For all CSV/PNG/metadata/profile files (approximately 2.6 GB):

```bash
python reproducibility/download.py --output Data/benchmark_tb --all
python reproducibility/verify.py --data-dir Data/benchmark_tb --assets
```

The downloader checks the fixed remote Git/LFS content identities. `verify.py --assets` checks local file presence.

## Length clarification

Let **N** be the number of sampled observations and **L=N−1** the number of sampling intervals. The generator specifies an end time `start + L × sampling_interval`, and the timestamp generator includes both endpoints. Consequently, L∈{1000,3000,5000,10000} produces N∈{1001,3001,5001,10001}.

The saved `metadata.total_length` contains N, while the existing difficulty classifier was called with L. Easy therefore means **L≤1000**, including the released N=1001 samples. This is an interval-count/sample-count naming distinction, not an undocumented additional Easy dataset. The exact conditions and observed counts are in [SPLITS_AND_DIFFICULTY.md](SPLITS_AND_DIFFICULTY.md).
