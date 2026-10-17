#!/usr/bin/env python3
"""Extract target-specific LLM predictions for the IaC security pilot."""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LABELS_PATH = ROOT / "dataset" / "labels.csv"
RAW_DIR = ROOT / "results" / "llm_raw"
OUTPUT_PATH = ROOT / "results" / "llm_predictions.csv"

# Each rule looks for evidence of the specific target issue.
TARGET_RULES = {
    "ssh_open_world": [
        r"ssh.{0,40}(open|unrestricted|world|all ip)",
        r"(0\.0\.0\.0/0).{0,80}(22|ssh)",
        r"(22|ssh).{0,80}0\.0\.0\.0/0",
    ],
    "s3_pab_disabled": [
        r"public.access.block.{0,50}(disabled|false)",
        r"(block_public_acls|block_public_policy|ignore_public_acls|restrict_public_buckets).{0,20}false",
    ],
    "ebs_encryption_disabled": [
        r"(encrypted|encryption).{0,30}(false|disabled|off)",
        r"(false|disabled|off).{0,30}(encrypted|encryption)",
    ],
    "iam_wildcard_permissions": [
        r"wildcard.{0,40}(iam|permission|action|resource)",
        r"action.{0,30}\*",
        r"resource.{0,30}\*",
    ],
    "s3_public_read_policy": [
        r"public.read",
        r"principal.{0,20}\*",
        r"public.{0,30}read",
    ],
    "rds_encryption_disabled": [
        r"(storage_encrypted|storage encryption|rds encryption).{0,30}(false|disabled|off)",
        r"(false|disabled|off).{0,30}(storage_encrypted|storage encryption|rds encryption)",
    ],
    "privileged_container": [
        r"privileged.{0,20}(true|enabled)",
        r"(true|enabled).{0,20}privileged",
    ],
    "container_runs_as_root": [
        r"(runasuser|uid).{0,20}(0|root)",
        r"running as root",
        r"runs as root",
    ],
    "host_network_enabled": [
        r"hostnetwork.{0,20}(true|enabled)",
        r"host networking.{0,20}(enabled|true)",
    ],
    "excessive_capabilities": [
        r"sys_admin",
        r"excessive.{0,20}capabilit",
    ],
    "privilege_escalation_enabled": [
        r"allowprivilegeescalation.{0,20}(true|enabled)",
        r"privilege escalation.{0,20}(permitted|enabled|allowed)",
    ],
    "writable_root_filesystem": [
        r"readonlyrootfilesystem.{0,20}false",
        r"writable root filesystem",
        r"root filesystem.{0,20}writable",
    ],
}


def target_detected(raw_result, target_id):
    parsed = raw_result.get("parsed_response")
    if not isinstance(parsed, dict):
        raise ValueError("Missing parsed_response")

    findings = parsed.get("findings")
    if not isinstance(findings, list):
        raise ValueError("Missing findings list")

    patterns = TARGET_RULES.get(target_id)
    if not patterns:
        raise ValueError(f"No rule defined for target_id: {target_id}")

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        text = " ".join(
            str(finding.get(field, ""))
            for field in ("issue", "evidence")
        ).lower()

        normalized = re.sub(r"[\s_.-]+", "", text)

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE) or re.search(
                pattern, normalized, re.IGNORECASE
            ):
                return 1

    return 0


def main():
    labels = pd.read_csv(LABELS_PATH, dtype=str, keep_default_na=False)
    predictions = []

    for row in labels.to_dict("records"):
        case_id = row["case_id"]
        target_id = row["target_id"]
        raw_path = RAW_DIR / f"{case_id}.json"

        if not raw_path.is_file():
            predictions.append({
                "case_id": case_id,
                "llm_detected": "",
                "status": "missing",
            })
            continue

        try:
            raw_result = json.loads(raw_path.read_text(encoding="utf-8"))
            detected = target_detected(raw_result, target_id)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"{case_id}: {error}", file=sys.stderr)
            predictions.append({
                "case_id": case_id,
                "llm_detected": "",
                "status": "invalid",
            })
            continue

        predictions.append({
            "case_id": case_id,
            "llm_detected": detected,
            "status": "scored",
        })

    output = pd.DataFrame(predictions)
    output.to_csv(OUTPUT_PATH, index=False)

    print(output.to_string(index=False))
    print(f"\nWrote {OUTPUT_PATH.relative_to(ROOT)}")
    print("Review target matches before calculating metrics.")


if __name__ == "__main__":
    main()
