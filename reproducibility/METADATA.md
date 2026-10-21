# Metadata specification for the fixed release

This specification describes the released JSONL and the existing code structures. The accompanying [JSON Schema](metadata.schema.json) describes the observed public test format. New descriptive fields are not silently inserted into the fixed test.

## Top-level test record

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Time-series sample ID; not a globally unique QA ID |
| `domain` | string | `coal_mill`, `pump`, `transformer`, `wind_turbine` |
| `source` | string | `synthetic` in this fixed release |
| `scenario_id` | string | Scenario identifier |
| `metadata` | object | Sample-level fields below |
| `timeseries_path` | string | CSV relative path; published paths contain Windows separators and a parent prefix |
| `ground_truth_events` | array | Zero or one recorded injected event per released sample |
| `qa_pairs` | array | L1–L4 QA records; a sample can have multiple L3 questions |

## Sample-level `metadata`

| Field | Type | Meaning |
| --- | --- | --- |
| `total_length` | integer | Actual number of observations T; {1001,3001,5001,10001} |
| `n_channels` | integer | Number of sensors N; 7 for coal mill/transformer; 8 for pump/wind turbine |
| `sampling_rate` | string | Sampling interval with its unit |
| `difficulty` | string | Easy/Medium/Hard/Expert encoded lowercase; computed using L=T−1 |
| `needle_ratio` | number | Recorded event-span ratio Σ(end−start)/L; current values are 0, 0.2, 1 |

The original generator argument and CSV filename `_L1000` refer to the interval count L, whereas saved `total_length=1001` refers to T. See [length and difficulty definitions](SPLITS_AND_DIFFICULTY.md). A future data format can introduce explicit `n_samples` / `n_intervals`; the fixed release is left unchanged here.

## Event record in `ground_truth_events`

| Field | Type | Meaning |
| --- | --- | --- |
| `type` | string | Programmed fault/anomaly type |
| `range` | two integers | Zero-based **[start,end)**; start included and end excluded |
| `severity` | string | `mild`, `moderate`, or `severe` |
| `affected_channels` | string array | Channel identifiers affected by the event |
| `causal_chain` | string array | Programmed propagation description, not independently measured causal proof |

The half-open convention is explicitly declared by `EventMetadata.time_range` in [`base.py`](../MultiAgentTS/scenarios/base.py); injection conditions and Python event slices use `start <= index < end`. Natural-language references may say “from start to end” without spelling out that convention. Use the metadata convention for programmatic span/count computations; do not reinterpret those prose endpoints to relabel the fixed benchmark. Thermal responses can persist outside an injection window; the metadata interval denotes the programmed event, not necessarily every downstream signal's complete recovery interval.

## QA record

| Field | Type | Meaning |
| --- | --- | --- |
| `level` | string | `L1`, `L2`, `L3`, `L4` |
| `question` | string | Exact model-visible question |
| `answer` | string | Reference response; not shown to the evaluated VLM |
| `reasoning_chain` | array | Recorded reasoning steps |
| `required_interval` | two integers or null | Event interval relevant to the QA; same half-open metadata convention |

There are 3023 null and 5389 list-valued `required_interval` entries. For matching prediction records, use sample ID + level + exact question, then verify `answer_gt` against the published `answer`. ID + level alone merges some distinct L3 questions.

## Per-sample `_metadata.json`

The richer generation metadata uses the dataclasses in [`base.py`](../MultiAgentTS/scenarios/base.py):

- `ChannelInfo`: `name`, `display_name`, `unit`, `normal_range`, optional high/low alarm thresholds, `physical_meaning`.
- `EventMetadata`: `event_type`, `fault_name`, `time_range`, `severity`, `parameters`, `affected_channels`, `causal_chain`, `description`.
- `GenerationMetadata`: scenario/domain names, length, sampling rate/seconds, channels, base/overall descriptions, injected events, generation seed, difficulty and ratio. The batch runner also records SNR fields.

Each CSV has matching `_eval.png`, `_metadata.json` and `_data_profile.json`. Profiles contain signal statistics used for QA generation. The evaluated VLM receives only the annotation-free chart and the question—not the event list, references or profiles.
