# IaC Security Evaluation — Pilot Results

## Objective

Evaluate whether an LLM can identify predefined security issues in synthetic Terraform and Kubernetes configurations. Compare target-specific detection with Checkov.

## Dataset

- Total cases: 24
- Terraform: 12 cases
- Kubernetes: 12 cases
- Positive cases: 12
- Target-negative controls: 12

Each target issue has one positive example and one target-negative control. Examples are synthetic and are not intended for deployment.

## Methods

### Checkov

- Version: 3.3.29
- Raw output: `results/checkov_v2/results_json.json`
- Checkov findings were mapped to target issues using predefined Checkov check IDs.
- Only matching failed checks counted as target detections. Unrelated findings were not counted.

### LLM

- Model: `claude-sonnet-5`
- Input: One configuration file per request
- Prompt: `prompts/llm_review.txt`
- Output: Structured findings containing issue, evidence, severity, and confidence
- Raw responses: `results/llm_raw/`
- The model was not given the ground-truth labels in its prompts.
- The API request used the model's default sampling behavior; deterministic output was not established.

## Scoring

A prediction of 1 means the method identified the predefined target issue. A prediction of 0 means it did not.

Additional findings outside the target issue were not counted as target detections. For example, unrestricted egress was not counted as detection of unrestricted inbound SSH.

TF002 tests whether S3 public-access-block protections are disabled. This configuration alone does not establish that the bucket is publicly accessible.

The negative cases are target-negative controls, not examples guaranteed to have no other security concerns.

## Preliminary Results

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

These are preliminary results on a small, deliberately constructed dataset. They do not establish general real-world performance or equivalence between Checkov and the LLM.

## Qualitative Observations

- The LLM identified the intended target issue in each positive case.
- It also reported additional concerns not included in the target-specific binary metrics.
- Checkov generated many findings unrelated to the target issue under test.
- Some LLM responses included additional findings that may be valid but require separate evaluation for correctness and relevance.

## Limitations and Scoring Risks

1. The dataset contains only 24 synthetic cases, with one positive and one negative example per target issue.
2. The examples are deliberately constructed and do not represent the diversity of real infrastructure.
3. The LLM prediction-matching rules were developed after inspecting the model responses. This creates a risk of confirmation bias and means the LLM scores are not an independent evaluation.
4. Checkov target predictions depend on a manually selected mapping of Checkov check IDs to target issues. That mapping requires review.
5. The binary metrics do not measure the correctness, completeness, severity, or usefulness of all reported findings.
6. One LLM run per case does not measure run-to-run variability.
7. The results do not establish that either method is generally more accurate or that the methods are equivalent.
8. Independent review and a preregistered scoring rubric are needed before drawing stronger conclusions.

## Conclusion

In this controlled 24-case pilot, the current scoring pipeline assigns identical target-specific metrics to Checkov and the LLM. Because the LLM matcher was created after its responses were inspected and the Checkov mapping was manually selected, these results should be treated as exploratory. A stronger follow-up should use a fixed scoring rubric, independent adjudication, broader cases, and repeated LLM runs.

## Reproducibility

- Ground-truth labels: `dataset/labels.csv`
- Terraform and Kubernetes examples: `dataset/examples/`
- Raw Checkov output: `results/checkov_v2/results_json.json`
- Target-specific Checkov predictions: `results/checkov_predictions.csv`
- Raw LLM responses: `results/llm_raw/`
- Target-specific LLM predictions: `results/llm_predictions.csv`
- Combined predictions: `results/predictions_final.csv`
- Metrics: `results/metrics_final.json`
- LLM prompt: `prompts/llm_review.txt`
- LLM runner: `scripts/run_llm_evaluation.py`
- LLM prediction extractor: `scripts/extract_llm_predictions.py`
- Metric evaluator: `scripts/evaluate.py`
