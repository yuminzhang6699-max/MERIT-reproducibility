# Final split and difficulty definitions

## Actual released split

The pinned dataset contains one split: `LongTS_Industrial/test.jsonl`. It includes all 1,716 series and 8,412 QA pairs; no training or validation subset is defined in this release. This is a fixed evaluation benchmark, not an inferred SFT train/validation partition.

The final construction path is [`pack_final_benchmark.py`](../pack_final_benchmark.py), which shuffles all source QA records with seed 42, removes obsolete split files from its output location, and writes a unified test. The original [`MultiAgentTS/benchmark_builder.py`](../MultiAgentTS/benchmark_builder.py) retains an earlier train/val/test/test-needle policy and is **not the final released split protocol**. Do not run it to reconstruct this fixed release.

The released `synthetic_qa_llm.jsonl` reproduces the unified test byte-for-byte after the final shuffle/path/newline transformations. See [packing evidence](evidence/packing_check.json).

## Sample points and intervals

T is the actual number of observations. L=T−1 is the number of sampling intervals passed to the original generator. Its timestamp range includes both endpoints. Saved `metadata.total_length` is T; the classifier uses L. The filename's `_L1000` consequently corresponds to T=1001.

For an event with zero-based half-open interval [s,e), the recorded span is e−s. The original ratio is ρ=Σ(e−s)/L, with ρ=0 when there is no injected event. Current samples contain at most one event, so no overlapping-event union rule is needed for this release.

## Exact original classifier, expressed with L

| Condition | Label |
| --- | --- |
| L≤1000 | Easy |
| 1000<L≤3000 and ρ>0.05 | Medium |
| 1000<L≤3000 and ρ≤0.05 | Hard |
| 3000<L≤5000 and ρ>0.03 | Hard |
| 3000<L≤5000 and ρ≤0.03 | Expert |
| L>5000 | Expert |

This is the function [`compute_difficulty`](../MultiAgentTS/scenarios/base.py), with the argument renamed descriptively in this document. The code and released labels have not been changed.

## Observed release counts

| Actual T | Interval count L | Label | Series |
| ---: | ---: | --- | ---: |
| 1001 | 1000 | Easy | 429 |
| 3001 | 3000 | Medium | 408 |
| 3001 | 3000 | Hard | 21 |
| 5001 | 5000 | Hard | 408 |
| 5001 | 5000 | Expert | 21 |
| 10001 | 10000 | Expert | 429 |

Total labels: Easy429, Medium408, Hard429, Expert450. All 1,716 labels match this classifier using L=T−1.

| Task | QA count |
| --- | ---: |
| L1 | 1716 |
| L2 | 1716 |
| L3 | 3264 |
| L4 | 1716 |

The 21 T=3001 Hard and 21 T=5001 Expert samples contain no injected event and are assigned by the classifier with ρ=0. The release contains 1620 samples at ρ=0.2, 84 at ρ=0, and 12 at ρ=1.
