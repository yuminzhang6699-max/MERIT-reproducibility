# Evaluation settings and exact prompts

## Public implementation

- VLM inference: [`run_benchmark_eval.py`](../run_benchmark_eval.py).
- HES judge/embedding/aggregation: [`benchmark_eval.py`](../benchmark_eval.py).
- Exact VLM, QA-generation and judge prompts: [PROMPTS.md](PROMPTS.md).

Model-visible input is one rendered multichannel chart plus one QA question. The loader normalizes Windows path separators and expands each sample's QA list. Reference answers and metadata are evaluation-side data.

## Evaluation parameters

| Setting | Public value |
| --- | --- |
| VLM temperature | 0.3 for non-Thinking models; the original runner omits it for listed Thinking models |
| Maximum generated tokens | 2048 |
| Judge | `qwen-plus`, temperature 0.1 |
| Embedding | `text-embedding-v3` |
| Direction D | aligned=1, partial=0.5, wrong=0 |
| Quality Q | (raw 1–5 rating − 1)/4 |
| HES | D × (0.4S + 0.6Q), S is cosine embedding similarity |
| Overall | Mean across evaluated QA responses; per-level/domain/difficulty also reported |
| Judge prompt truncation | Question500 characters, reference1000, prediction1000 |
| Rendering | 16×2.5n-inch vertical subplots, 150DPI, line width1.2, English channel labels, no fault highlights |

`bbox_inches='tight'` may slightly change saved PNG pixel width with tick labels. Do not equate nominal canvas width with guaranteed processor-visible resolution. Serving processor pixel/token settings must be recorded separately.

## Run a new evaluation

First obtain all fixed data with `download.py --all`, a serving environment supporting the original model, and judge/embedding credentials. Set `VLM_BASE_URL` and `VLM_API_KEY` for your OpenAI-compatible model service and configure the DashScope key used by `benchmark_eval.py`. `.env` files are not automatically loaded by the original Python entry points; export variables in the shell. Do not commit credentials or share unredacted logs (the original runner displays a key prefix).

From the repository root:

```bash
python run_benchmark_eval.py \
  --models qwen3-vl-32b-instruct \
  --benchmark-dir Data/benchmark_tb/LongTS_Industrial \
  --data-dir Data/benchmark_tb \
  --results-dir results/reproduction_fixed_release \
  --split test --sequential --workers 1
```

The model argument is the original service ID. When using local Hugging Face weights, configure the server's served model name to match and record the actual weight path/revision. The example uses `--workers 1` for sequential execution. Do not change precision, model family, image preprocessing or prompts without documenting the deviation.

The original script saves predictions, detailed scores and summaries. Retain raw judge output, errors/retries, model/processor versions, actual image identities, package export and command line for the new run.
