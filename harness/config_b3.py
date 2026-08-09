"""
Basanos-3 config. Extends the existing harness/config.py conventions:
  - Same .env path (~/hive/.env)
  - Same RELIAGENT_URL default (localhost:8124/run)
  - Adds OPENAI_API_KEY loading
  - Fixes CLAUDE_MODEL to claude-haiku-4-5-20251001 for Basanos-3's Haiku arm
  - Experiment numbering starts at 018 (next after Basanos-2's experiment_017)

Basanos-3 experiment map:
  018: hallucination       / gpt-5.6-luna
  019: hallucination       / gpt-5.6-terra
  020: hallucination       / claude-haiku-4-5-20251001
  021: sycophantic_gap_fill / gpt-5.6-luna
  022: sycophantic_gap_fill / gpt-5.6-terra
  023: sycophantic_gap_fill / claude-haiku-4-5-20251001
  024: confidence_collapse / gpt-5.6-luna
  025: confidence_collapse / gpt-5.6-terra
  026: confidence_collapse / claude-haiku-4-5-20251001
  027: context_degradation / gpt-5.6-luna
  028: context_degradation / gpt-5.6-terra
  029: context_degradation / claude-haiku-4-5-20251001
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(os.environ.get("HIVE_ENV_PATH", Path.home() / "hive" / ".env"))
load_dotenv(ENV_PATH)

# ReliAgent endpoint — same default as existing harness
RELIAGENT_URL = os.environ.get("RELIAGENT_RUN_URL", "http://localhost:8124/run")

# Results land in the existing reliagent-benchmark/results/ tree so the
# no-overwrite/append-only convention and rebuild_summary.py are all reused.
RESULTS_DIR = Path(
    os.environ.get(
        "HARNESS_RESULTS_DIR",
        Path.home() / "hive" / "reliagent-benchmark" / "results",
    )
)

# Basanos-3 model strings
HAIKU_MODEL  = "claude-haiku-4-5-20251001"
LUNA_MODEL   = "gpt-5.6-luna"
TERRA_MODEL  = "gpt-5.6-terra"

# Experiment number → (detector, provider, model)
EXPERIMENT_MAP = {
    18: ("hallucination",        "openai",     LUNA_MODEL),
    19: ("hallucination",        "openai",     TERRA_MODEL),
    20: ("hallucination",        "anthropic",  HAIKU_MODEL),
    21: ("sycophantic_gap_fill", "openai",     LUNA_MODEL),
    22: ("sycophantic_gap_fill", "openai",     TERRA_MODEL),
    23: ("sycophantic_gap_fill", "anthropic",  HAIKU_MODEL),
    24: ("confidence_collapse",  "openai",     LUNA_MODEL),
    25: ("confidence_collapse",  "openai",     TERRA_MODEL),
    26: ("confidence_collapse",  "anthropic",  HAIKU_MODEL),
    27: ("context_degradation",  "openai",     LUNA_MODEL),
    28: ("context_degradation",  "openai",     TERRA_MODEL),
    29: ("context_degradation",  "anthropic",  HAIKU_MODEL),
}

# Provenance strings for the new model arms
# (same source as Basanos-2, new model = same published-instrument category)
PROVENANCE = {
    "hallucination": (
        "published-instrument (indirect -- Rao et al. arXiv:2604.03173 methodology; "
        "ExpertQA selected for Phase 2 Track A, cmalaviya/expertqa 'main' split)"
    ),
    "sycophantic_gap_fill": (
        "published-instrument (direct -- agent-consistency's own repo, "
        "tasks + tools + runner; Abelo9996/agent-consistency, arXiv:2605.28840)"
    ),
    "confidence_collapse": (
        "published-instrument (direct -- sycophancy-eval, "
        "meg-tong/sycophancy-eval, are_you_sure.jsonl; "
        "same source as Phase 1 experiment_007)"
    ),
    "context_degradation": (
        "published-instrument (direct -- Lost in the Middle's own "
        "prompting.py/metrics.py, real qa_data; nelson-liu/lost-in-the-middle)"
    ),
}


def get_openai_api_key() -> str:
    val = os.environ.get("OPENAI_API_KEY")
    if not val:
        raise RuntimeError(
            f"OPENAI_API_KEY not found in {ENV_PATH}. "
            f"Add a line: OPENAI_API_KEY=sk-..."
        )
    return val


def get_anthropic_api_key() -> str:
    val = os.environ.get("ANTHROPIC_API_KEY")
    if not val:
        raise RuntimeError(
            f"ANTHROPIC_API_KEY not found in {ENV_PATH}. "
            f"Add a line: ANTHROPIC_API_KEY=sk-ant-..."
        )
    return val
