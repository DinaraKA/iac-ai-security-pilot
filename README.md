# IaC AI Security Pilot

An empirical pilot comparing Checkov static analysis with an LLM-based security review of synthetic Terraform and Kubernetes configurations.

## Research Question

Can an LLM identify predefined Infrastructure-as-Code (IaC) security issues, and how do its results compare with Checkov on the same labeled examples?

## Dataset and Scope

- 24 synthetic cases: 12 Terraform and 12 Kubernetes.
- 12 positive cases containing predefined target issues and 12 target-negative controls.
- 12 target issue categories, each represented by a positive case and a paired negative control.
- No production infrastructure, customer data, or cloud credentials are included in the dataset.
- Results are exploratory and are not a general security benchmark.

## Methods

- **Static analysis:** Checkov.
- **LLM review:** Claude Sonnet 5, with one configuration per request.
- **Scoring:** Target-specific binary predictions. Unrelated findings do not count as detections of the predefined target issue.
- **Metrics:** Precision, recall, F1 score, true positives, false positives, false negatives, and true negatives.

The S3 public-access-block case tests disabled protections. This condition alone does not prove that a bucket is publicly accessible.

## Repository Structure

- `dataset/examples/` — synthetic Terraform and Kubernetes configurations.
- `dataset/labels.csv` — case labels and predefined target issues.
- `prompts/llm_review.txt` — standardized LLM review prompt.
- `scripts/run_llm_evaluation.py` — runs the LLM review and saves raw responses.
- `scripts/extract_llm_predictions.py` — extracts target-specific LLM predictions.
- `scripts/evaluate.py` — calculates evaluation metrics.
- `results/llm_raw/` — raw LLM responses.
- `results/checkov_v2/results_json.json` — saved Checkov scan output.
- `results/checkov_predictions.csv` — target-specific Checkov predictions.
- `results/llm_predictions.csv` — target-specific LLM predictions.
- `results/predictions_final.csv` — combined predictions used for metric calculation.
- `results/metrics_final.json` — calculated metrics.
- `results/notes.md` — methodology, results, observations, and limitations.
- `tests/` — automated tests.

## Setup

Tested on macOS with Python 3.12 and a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Checkov if it is not already installed:

```bash
python -m pip install checkov
```

## Run the Evaluation

Set `ANTHROPIC_API_KEY` in your terminal environment before running the LLM evaluation. Never commit API keys or other secrets.

Run the LLM review:

```bash
python scripts/run_llm_evaluation.py
```

The runner saves raw responses and can reuse valid saved results to avoid unnecessary API requests.

The current prediction files contain target-specific scoring results. Review the labels, raw responses, and Checkov findings before relying on the predictions. The scoring rules and mappings require independent review.

Calculate metrics from the combined predictions:

```bash
python scripts/evaluate.py --predictions results/predictions_final.csv --out results/metrics_final.json
```

Run automated tests:

```bash
python -m pytest -q
```

## Preliminary Results

The current exploratory scoring reports the following results on 24 cases:

| Metric | Checkov | LLM |
|---|---:|---:|
| Cases scored | 24 | 24 |
| True positives | 12 | 12 |
| False positives | 0 | 0 |
| False negatives | 0 | 0 |
| True negatives | 12 | 12 |
| Precision | 1.00 | 1.00 |
| Recall | 1.00 | 1.00 |
| F1 score | 1.00 | 1.00 |

**These metrics are not independently validated.** The LLM matching rules and Checkov check-ID mapping were developed after examining the cases and outputs. This creates a risk of confirmation bias and may inflate apparent performance.

The results describe this scoring procedure on a small, deliberately constructed dataset. They do not establish real-world accuracy, superiority, or equivalence between the methods.

## Limitations

- Only 24 synthetic cases were evaluated.
- Each target issue is represented by a limited number of examples.
- Each LLM case was evaluated once; repeatability was not measured.
- Default sampling behavior was used; deterministic output was not established.
- Unrelated security findings are excluded from target-specific metrics.
- Labels and scoring mappings need independent review.
- The dataset does not represent the full range of real-world IaC configurations.
- Disabled S3 public-access-block protections do not, by themselves, establish public bucket access.

## Research Integrity and Next Steps

Raw model responses, labels, predictions, and calculated metrics are retained to support inspection and reproducibility.

Next steps include independent review of labels and scoring rules, blinded assessment of model findings, additional diverse configurations and negative controls, and repeated LLM runs to evaluate consistency.