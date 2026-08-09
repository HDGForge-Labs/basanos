"""
Basanos-3 results writer. Extends harness/results.py with model and provider
fields in every trial record and summary, enabling cross-model comparison in
the final Basanos-3 report.

Convention: experiment directories for Basanos-3 are named experiment_018
through experiment_029, continuing the existing numbered sequence in
reliagent-benchmark/results/. The existing next_experiment_dir() logic in
results.py handles numbering automatically — we reuse it here but write
richer records.

Trial record shape (superset of Basanos-2 shape):
  timestamp_utc, detector, model, provider, provenance, source_citation,
  elicitation_input, llm_generation, reliagent_request, reliagent_response,
  hypothesis, trial_type (clean|violation), passed, notes
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from harness.results import next_experiment_dir  # reuse numbering logic
from harness.config_b3 import RESULTS_DIR


def write_trial_b3(
    exp_dir: Path,
    trial_index: int,
    detector: str,
    model: str,
    provider: str,
    provenance: str,
    source_citation: str,
    trial_type: str,           # "clean" or "violation"
    elicitation_input: dict,
    llm_generation: dict,
    reliagent_call: dict,
    hypothesis: str,
    passed: bool,
    notes: str = "",
) -> Path:
    """
    Writes one trial JSON. trial_type is "clean" (expected pass) or
    "violation" (expected detection). passed=True means ReliAgent behaved
    correctly for this trial_type:
      - clean trial:     passed=True  → no false positive (correct)
      - violation trial: passed=True  → detector fired    (correct)
    """
    if trial_type not in ("clean", "violation"):
        raise ValueError(f"trial_type must be 'clean' or 'violation', got '{trial_type}'")

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "detector": detector,
        "model": model,
        "provider": provider,
        "provenance": provenance,
        "source_citation": source_citation,
        "trial_type": trial_type,
        "elicitation_input": elicitation_input,
        "llm_generation": {
            "model": llm_generation.get("model"),
            "text": llm_generation.get("text"),
            "latency_ms": llm_generation.get("latency_ms"),
            "input_tokens": llm_generation.get("input_tokens"),
            "output_tokens": llm_generation.get("output_tokens"),
        },
        "reliagent_request": reliagent_call["request"],
        "reliagent_response": reliagent_call["response"],
        "hypothesis": hypothesis,
        "passed": passed,
        "notes": notes,
    }

    out_path = exp_dir / f"trial_{trial_index:03d}.json"
    out_path.write_text(json.dumps(record, indent=2))
    return out_path


def write_summary_b3(
    exp_dir: Path,
    detector: str,
    model: str,
    provider: str,
    trial_results: list[dict],
) -> Path:
    """
    Writes experiment summary.json. trial_results is a list of per-trial
    dicts with at minimum: trial_file, trial_type, passed.
    Computes clean/violation pass rates separately for TPR/FPR calculation.
    """
    n_total = len(trial_results)
    n_passed = sum(1 for t in trial_results if t["passed"])

    clean_trials = [t for t in trial_results if t.get("trial_type") == "clean"]
    violation_trials = [t for t in trial_results if t.get("trial_type") == "violation"]

    n_clean = len(clean_trials)
    n_violation = len(violation_trials)
    n_clean_passed = sum(1 for t in clean_trials if t["passed"])
    n_violation_passed = sum(1 for t in violation_trials if t["passed"])

    # FPR = proportion of clean trials that incorrectly fired (passed=False for clean)
    # TPR = proportion of violation trials that correctly fired (passed=True for violation)
    fpr = round(1 - (n_clean_passed / n_clean), 4) if n_clean else None
    tpr = round(n_violation_passed / n_violation, 4) if n_violation else None

    summary = {
        "detector": detector,
        "model": model,
        "provider": provider,
        "experiment_dir": exp_dir.name,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_trials": n_total,
        "n_clean": n_clean,
        "n_violation": n_violation,
        "n_clean_passed": n_clean_passed,
        "n_violation_passed": n_violation_passed,
        "overall_pass_rate": round(n_passed / n_total, 4) if n_total else None,
        "true_positive_rate": tpr,
        "false_positive_rate": fpr,
        "trials": trial_results,
    }

    out_path = exp_dir / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2))
    return out_path
