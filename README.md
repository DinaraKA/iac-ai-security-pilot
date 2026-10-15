# IaC AI Security Pilot

A small empirical pilot comparing Checkov static analysis with an LLM's security review of synthetic Terraform and Kubernetes configurations.

## Research question

Can an LLM identify predefined Infrastructure-as-Code security issues, and how do its results compare with Checkov on the same labeled examples?

## Scope and safety

- Six synthetic examples: three Terraform and three Kubernetes.
- Four positive cases and two target-negative controls.
- No production infrastructure, cloud credentials, or customer data.
- Results are preliminary and are not a general benchmark.

## Repository layout

- `dataset/` — synthetic configurations and ground-truth labels.
- `prompts/llm_review.txt` — standardized LLM review prompt.
- `scripts/run_llm_evaluation.py` — runs the LLM evaluation and saves raw responses.
- `scripts/evaluate.py` — calculates target-specific evaluation metrics.
- `tests/` — automated tests.
- `results/llm_raw/` — raw LLM responses.
- `results/predictions.csv` — manually reviewed binary predictions.
- `results/metrics.json` — calculated metrics.
- `results/notes.md` — methodology, observations, and limitations.
- `results/checkov/` — saved Checkov output.

## Setup

Tested on macOS with Python and a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Checkov if needed:

```bash
python -m pip install checkov
```

Run the baseline scan:

```bash
checkov -d dataset/examples --framework terraform,kubernetes --output cli
```

## Run the evaluation

Set `ANTHROPIC_API_KEY` in your terminal environment before running the LLM evaluation. Do not commit API keys or other secrets.

Run the LLM evaluation:

```bash
python scripts/run_llm_evaluation.py
```

The runner saves raw responses and can reuse valid saved results rather than making duplicate API requests.

Review the model findings and update `results/predictions.csv` only after determining whether each method identified the specific issue defined in `dataset/labels.csv`.

Calculate the metrics:

```bash
python scripts/evaluate.py
```

Run the tests:

```bash
python -m pytest -q
```

## Pilot results

| Metric | Checkov | LLM |
|---|---:|---:|
| Cases scored | 6 | 6 |
| True positives | 4 | 4 |
| False positives | 0 | 0 |
| False negatives | 0 | 0 |
| True negatives | 2 | 2 |
| Precision | 1.00 | 1.00 |
| Recall | 1.00 | 1.00 |
| F1 score | 1.00 | 1.00 |

Both methods identified all four predefined target issues and did not flag either target-negative control for its target issue.

These results are specific to this small, deliberately constructed dataset. They do not establish real-world accuracy, superiority, or equivalence between the methods.

## Limitations

- Only six synthetic cases were evaluated.
- There were only two target-negative controls.
- Each LLM case was evaluated once.
- Additional findings were not included in the target-specific binary metrics.
- The LLM used default sampling behavior; deterministic output was not established.
- Ground-truth labels and manual scoring decisions need independent review.
- The S3 example tests disabled public-access-block protections; it does not, by itself, prove that a bucket is publicly accessible.

## Research integrity

The project preserves raw model responses, labels, scored predictions, and calculated metrics to support review and reproducibility. Manual scoring decisions should be documented, and conclusions should remain proportional to the available evidence.

The next stage is to expand the dataset with more diverse configurations, additional negative controls, and independent review of the labels.