
# IaC Security Evaluation — Pilot Results

## Objective

Evaluate whether an LLM can identify predefined security issues in synthetic Terraform and Kubernetes configurations. Compare its target-issue detection with Checkov.

## Dataset

- Total cases: 6
- Terraform: 3 cases
- Kubernetes: 3 cases
- Positive cases: 4
- Target-negative controls: 2

The examples are synthetic and are not intended for deployment.

## Methods

### Checkov

Checkov was run against the configuration examples. Findings were mapped to the predefined target issues for each case.

### LLM

- Model: `claude-sonnet-5`
- Input: One configuration file per request
- Prompt: `prompts/llm_review.txt`
- Output: Structured findings containing issue, evidence, severity, and confidence
- Review: Raw responses were saved and reviewed before assigning binary target-detection scores.

The model did not receive the ground-truth labels in its prompts. The API request used the model's default sampling behavior because the installed SDK rejected the `temperature` argument.

## Scoring

A prediction of 1 means the method identified the predefined target issue for that case. A prediction of 0 means it did not.

Additional findings outside the target issue were not counted as target detections. For example, unrestricted egress in TF003 was not counted as a detection of unrestricted inbound SSH.

TF002 tests whether S3 public-access-block protections are disabled. This configuration alone does not establish that the bucket is publicly accessible.

The two negative controls are target-negative controls, not examples guaranteed to have no possible security concerns.

## Results

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

Both methods detected all four predefined target issues and did not flag either target-negative control for its target issue.

## Qualitative observations

- The LLM identified the intended SSH, S3 public-access-block, privileged-container, and root-container issues.
- It also reported additional concerns involving unrestricted egress, S3 encryption and versioning, resource limits, and seccomp configuration.
- These additional findings were not included in the target-specific binary metrics.
- The LLM returned JSON wrapped in Markdown code fences for TF001. The response was recovered and parsed from the saved raw output without repeating that API request.

## Limitations

1. Six synthetic cases are insufficient to estimate real-world detection performance.
2. The examples were deliberately constructed around known target issues and are not representative of the full variety of infrastructure configurations.
3. Only two target-negative controls were evaluated.
4. Binary target-specific scoring does not evaluate the correctness, completeness, severity, or usefulness of all reported findings.
5. One LLM run per case does not measure run-to-run variability.
6. The LLM used default sampling behavior; fully deterministic output was not established.
7. The results do not establish that either method is generally more accurate or that the methods are equivalent.
8. The target labels and manual scoring decisions should be independently reviewed before a larger evaluation.

## Conclusion

In this six-case pilot, Checkov and the LLM achieved identical target-specific metrics. This establishes a baseline for a larger evaluation, not a general claim about either method's effectiveness.

## Reproducibility

- Ground-truth labels: `dataset/labels.csv`
- Raw LLM responses: `results/llm_raw/`
- Scored predictions: `results/predictions.csv`
- Calculated metrics: `results/metrics.json`
- LLM prompt: `prompts/llm_review.txt`
- LLM runner: `scripts/run_llm_evaluation.py`
- Metric evaluator: `scripts/evaluate.py`
