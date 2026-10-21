# Generation and final benchmark construction

## Existing release entry points

The actual released programmatic scenario path is:

1. [`batch_runner_tb.py`](../MultiAgentTS/scenarios/batch_runner_tb.py): directly calls the coal-mill, pump, transformer and wind-turbine TimeBlender scenario functions. Generates numeric CSVs, structured metadata, SNR values and annotation-free evaluation charts.
2. [`compute_data_profiles.py`](../compute_data_profiles.py): computes global/normal/event statistics used by QA generation.
3. [`qa_llm_generator.py`](../MultiAgentTS/scenarios/qa_llm_generator.py): uses metadata and the statistics to generate L1–L4 QA through `LLMQAGenerator` (public default: `qwen3-max`, temperature 0.7, max_tokens 4096).
4. [`pack_final_benchmark.py`](../pack_final_benchmark.py): shuffles the full source QA with seed 42 and creates a unified test set. It is distinct from the legacy train/val/test builder.

Scenario implementations: [coal mill](../MultiAgentTS/scenarios/coal_mill_tb.py), [pump](../MultiAgentTS/scenarios/pump_tb.py), [transformer](../MultiAgentTS/scenarios/transformer_tb.py), [wind turbine](../MultiAgentTS/scenarios/wind_turbine_tb.py). The engine is in [`time_blender/`](../time_blender/).

The batch-generation configuration is 143 scenarios × four interval lengths {1000,3000,5000,10000} × seeds {42,123,789} = 1,716 series. The published [generation manifest](evidence/generation_manifest.json) records 1716 generated, 0 skipped and 0 errors. The released path uses predefined executable scenario functions.

## Reproduce the fixed release versus generate a new instance

For experiments comparable to the published references, download the **fixed released test and images**, rather than replacing the QA with a newly generated version. The [top-level guide](README.md) gives the fixed-download and deterministic-repacking commands.

Generating new waveforms/QA is a separate operation. It requires compatible scientific/API dependencies and a valid DashScope key. Record the execution environment and QA model version for each generation run.

## Stage-based helper

From the repository root, first inspect the plan:

```bash
python reproducibility/run_pipeline.py --stage all --data-dir Data/rebuilt_merit --plan
```

Install dependencies in an isolated environment:

```bash
python -m pip install -r requirements.txt
```

Then execute stages, keeping the frozen release in `Data/benchmark_tb` separate:

```bash
python reproducibility/run_pipeline.py --stage synthesize --data-dir Data/rebuilt_merit
python reproducibility/run_pipeline.py --stage profile --data-dir Data/rebuilt_merit

# Configure DASHSCOPE_API_KEY privately before the API-backed stage.
python reproducibility/run_pipeline.py --stage qa --data-dir Data/rebuilt_merit
python reproducibility/run_pipeline.py --stage pack --data-dir Data/rebuilt_merit
```

The helper passes the QA API key explicitly to the existing function. This avoids the original QA CLI's fallback to an unprovided `configs/config.yaml`; copying `.env.example` alone does not load environment variables into Python automatically.

`--stage all` executes the same four stages in order. It checks for the QA key before starting, refuses to combine new QA with an existing QA file, and refuses to overwrite an existing final test file.

The portable pack helper reproduces the original producer's Windows `..\\domain\\file.csv` paths and CRLF newlines. This yields the published test digest from the published source QA on either Linux or Windows. The existing evaluation loader normalizes these path separators. It does not change the QA or split policy.

## Artifacts to preserve for a new run

Record the source code commit, full configuration, actual dependency export, seed, generator manifest, complete metadata and profiles, exact QA model/version/date, raw QA output, audit failures and repairs, final split digest and input-image digests. Keep the immutable released data version as a separate baseline.
