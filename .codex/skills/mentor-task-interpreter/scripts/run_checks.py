#!/usr/bin/env python3
"""Run the skill's deterministic smoke checks without third-party dependencies."""
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "scripts" / "validate_task_spec.py"
FIXTURE = ROOT / "fixtures" / "meeting-summary.task-spec.json"
GOLDEN_FIXTURE = ROOT / "fixtures" / "golden-case.task-spec.json"


def run(command):
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.returncode:
        print(completed.stdout + completed.stderr, file=sys.stderr, end="")
        raise SystemExit(completed.returncode)
    print(completed.stdout, end="")


def main():
    run([sys.executable, str(VALIDATOR), str(FIXTURE)])
    run([sys.executable, str(VALIDATOR), str(GOLDEN_FIXTURE)])
    invalid = json.loads(FIXTURE.read_text(encoding="utf-8"))
    invalid.pop("task_goal")
    probe = ROOT / "fixtures" / ".invalid-task-spec.json"
    try:
        probe.write_text(json.dumps(invalid, ensure_ascii=False), encoding="utf-8")
        failed = subprocess.run([sys.executable, str(VALIDATOR), str(probe)], cwd=ROOT, capture_output=True, text=True)
        if failed.returncode == 0:
            print("Expected invalid fixture to fail", file=sys.stderr)
            return 1
        if "missing required field 'task_goal'" not in failed.stderr:
            print(f"Unexpected validation error: {failed.stderr}", file=sys.stderr)
            return 1
    finally:
        probe.unlink(missing_ok=True)
    invalid_order = json.loads(GOLDEN_FIXTURE.read_text(encoding="utf-8"))
    invalid_order["execution_order"][0]["evidence_ids"] = ["unknown-evidence"]
    probe = ROOT / "fixtures" / ".invalid-execution-order.task-spec.json"
    try:
        probe.write_text(json.dumps(invalid_order, ensure_ascii=False), encoding="utf-8")
        failed = subprocess.run([sys.executable, str(VALIDATOR), str(probe)], cwd=ROOT, capture_output=True, text=True)
        if failed.returncode == 0 or "unknown evidence ID 'unknown-evidence'" not in failed.stderr:
            print(f"Execution-order evidence was not rejected: {failed.stderr}", file=sys.stderr)
            return 1
    finally:
        probe.unlink(missing_ok=True)
    print("PASS: smoke and golden fixtures accepted; invalid required field and execution-order evidence rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
