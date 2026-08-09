"""
Calls ReliAgent's real /run contract, per core.py (task #443):
required: tool_name, parameters, response, latency_ms
optional: token_count, context_window_used, confidence_score, expected_schema,
          response_grounded_in_parameters

caller_ip: simulates a distinct calling agent/session via the X-Forwarded-For
header, which app.py's _get_caller_ip() reads. This matters for benchmark
trials specifically: ReliAgent tracks call history per caller to detect real
drift/repetition within one agent's session. Without a distinct caller_ip per
trial, every trial in a run looks like one continuous session to ReliAgent,
and unrelated trials (different questions, different detectors under test)
get misread as parameter drift or repetition within that fake session. Real
bug caught 2026-07-17: trial 2 of the first pilot run was flagged
"parameter_drift" instead of being cleanly evaluated for hallucination,
because it had no caller_ip and shared history with trial 1.

response_grounded_in_parameters: opt-in flag (default False) that enables
ReliAgent's hedge+numeric hallucination check. Set True only when the tool's
response values should be fully traceable to its input parameters. See
core.py lines 774-794 for the full rationale.

_normalize_text: strips Unicode typographic punctuation (curly quotes, em-dash)
to ASCII equivalents before sending to ReliAgent. Required for cross-model
consistency: reasoning models (Luna, Terra) output curly quotes (\u2018\u2019)
which break ReliAgent's ASCII regex patterns. Confirmed root cause of
sycophantic_gap_fill TPR=0 on Luna: "You\u2019re" didn't match "you('re| are)".
"""
import requests
from harness.config import RELIAGENT_URL


def _normalize_text(text: str) -> str:
    """Normalize Unicode typographic punctuation to ASCII for regex compatibility."""
    replacements = {
        "\u2018": "'",    # left single quotation mark
        "\u2019": "'",    # right single quotation mark
        "\u201c": '"',    # left double quotation mark
        "\u201d": '"',    # right double quotation mark
        "\u2014": "-",    # em dash
        "\u2013": "-",    # en dash
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",    # non-breaking space
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text


def run(
    tool_name: str,
    parameters: dict,
    response_text: str,
    latency_ms: float,
    token_count: int | None = None,
    context_window_used: float | None = None,
    confidence_score: float | None = None,
    expected_schema: dict | None = None,
    caller_ip: str | None = None,
    response_grounded_in_parameters: bool = False,
    timeout_s: float = 30.0,
) -> dict:
    # Normalize Unicode typographic punctuation so ReliAgent's ASCII regex
    # patterns match consistently across all LLM providers.
    response_text = _normalize_text(response_text)

    payload = {
        "tool_name": tool_name,
        "parameters": parameters,
        "response": response_text,
        "latency_ms": latency_ms,
    }
    if token_count is not None:
        payload["token_count"] = token_count
    if context_window_used is not None:
        payload["context_window_used"] = context_window_used
    if confidence_score is not None:
        payload["confidence_score"] = confidence_score
    if expected_schema is not None:
        payload["expected_schema"] = expected_schema
    if response_grounded_in_parameters:
        payload["response_grounded_in_parameters"] = True

    headers = {}
    if caller_ip:
        headers["X-Forwarded-For"] = caller_ip

    resp = requests.post(RELIAGENT_URL, json=payload, headers=headers, timeout=timeout_s)
    resp.raise_for_status()
    return {"request": payload, "response": resp.json()}
