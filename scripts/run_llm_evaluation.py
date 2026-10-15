
#!/usr/bin/env python3
"""Collect LLM findings for a controlled IaC security evaluation."""

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "llm_review.txt"
LABELS_PATH = ROOT / "dataset" / "labels.csv"
RAW_DIR = ROOT / "results" / "llm_raw"
MODEL = "claude-sonnet-5"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def parse_response_json(raw_text):
    """Parse JSON returned directly or inside Markdown code fences."""
    text = raw_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    parsed = json.loads(text)

    if not isinstance(parsed, dict) or not isinstance(
        parsed.get("findings"), list
    ):
        raise ValueError("Expected JSON object with a findings list.")

    return parsed



def load_existing_result(path, case_id):
    """Load a saved result and recover JSON from its original response."""
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        sys.exit(
            f"Cannot read existing output for {case_id}: {path}\n"
            "Inspect the file before retrying."
        )

    if not isinstance(result, dict) or result.get("case_id") != case_id:
        sys.exit(f"Unexpected saved result for {case_id}: {path}")

    parsed = result.get("parsed_response")

    if not (
        isinstance(parsed, dict)
        and isinstance(parsed.get("findings"), list)
    ):
        try:
            parsed = parse_response_json(result.get("response_text", ""))
        except (json.JSONDecodeError, ValueError):
            sys.exit(
                f"Cannot recover JSON for {case_id}: {path}\n"
                "Inspect the saved response before retrying."
            )

        result["parsed_response"] = parsed
        result.pop("parse_error", None)
        path.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )

    return result



def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set in this terminal.")

    if not PROMPT_PATH.is_file() or not LABELS_PATH.is_file():
        sys.exit("Prompt or labels file is missing.")

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    if "[PASTE ONE FILE HERE]" not in prompt_template:
        sys.exit("Prompt template is missing its configuration placeholder.")

    labels = read_csv(LABELS_PATH)
    case_ids = [row["case_id"] for row in labels]

    if not labels or len(case_ids) != len(set(case_ids)):
        sys.exit("Labels must contain unique case IDs.")

    # Validate every input before making any API calls.
    configurations = {}
    for label in labels:
        path = ROOT / label["file"]
        if not path.is_file():
            sys.exit(f"Configuration file not found: {label['file']}")
        configurations[label["case_id"]] = path.read_text(encoding="utf-8")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Resume completed cases instead of paying for them again.
    completed = {}
    for case_id in case_ids:
        path = RAW_DIR / f"{case_id}.json"
        if path.exists():
            completed[case_id] = load_existing_result(path, case_id)

    client = anthropic.Anthropic()

    for label in labels:
        case_id = label["case_id"]
        raw_path = RAW_DIR / f"{case_id}.json"

        if case_id in completed:
            print(f"Skipping {case_id}: valid saved result exists.")
            continue

        config = configurations[case_id]
        prompt = prompt_template.replace(
            "[PASTE ONE FILE HERE]", config
        )

        print(f"Evaluating {case_id}...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = "\n".join(
            block.text
            for block in response.content
            if block.type == "text"
        ).strip()

        result = {
            "case_id": case_id,
            "model": MODEL,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "response_id": response.id,
            "response_text": raw_text,
        }

        try:
            parsed = parse_response_json(raw_text)
            if (
                not isinstance(parsed, dict)
                or not isinstance(parsed.get("findings"), list)
            ):
                raise ValueError(
                    "Expected a JSON object containing a findings list."
                )

            result["parsed_response"] = parsed

        except (json.JSONDecodeError, ValueError) as error:
            result["parse_error"] = str(error)
            raw_path.write_text(
                json.dumps(result, indent=2) + "\n",
                encoding="utf-8",
            )
            sys.exit(
                f"{case_id}: response was not valid expected JSON. "
                f"Saved for inspection at {raw_path}."
            )

        # Save immediately so completed calls survive a later failure.
        raw_path.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )
        completed[case_id] = result
        print(f"  Saved {raw_path.relative_to(ROOT)}")

    print(f"\nModel: {MODEL}")
    print(f"Completed cases: {len(completed)}/{len(labels)}")
    print(f"Raw findings: {RAW_DIR.relative_to(ROOT)}/")
    print("No predictions were assigned or modified.")
    print("Review findings before scoring the results.")


if __name__ == "__main__":
    main()
