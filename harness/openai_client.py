"""
Calls the OpenAI API to generate the response text ReliAgent will evaluate.
Parallel to anthropic_client.py -- same return shape:
  {text, latency_ms, input_tokens, output_tokens, model}

Supports gpt-5.6-luna and gpt-5.6-terra. Both require:
  - reasoning_effort="none" to disable extended thinking (incompatible with
    function calling and adds latency/cost with no benefit for this use case)
  - max_completion_tokens (not max_tokens) for models in the o-series / new
    generation API contract

API key: OPENAI_API_KEY in ~/hive/.env (same file as all other Hive secrets).
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ENV_PATH = Path(os.environ.get("HIVE_ENV_PATH", Path.home() / "hive" / ".env"))
load_dotenv(ENV_PATH)

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                f"OPENAI_API_KEY not found in {ENV_PATH}. "
                f"Add a line: OPENAI_API_KEY=sk-..."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def generate(
    prompt: str,
    model: str,
    max_completion_tokens: int = 1024,
    system: str | None = None,
) -> dict:
    """
    Single-turn generation. Returns dict with:
      text, latency_ms, input_tokens, output_tokens, model

    reasoning_effort="none" is set unconditionally -- Luna/Terra with reasoning
    enabled produces unexpectedly verbose outputs and burns budget with no
    benefit for eliciting tool-call style responses ReliAgent evaluates.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = _get_client()

    kwargs = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_completion_tokens,
        "reasoning_effort": "none",
    }

    start = time.monotonic()
    response = client.chat.completions.create(**kwargs)
    latency_ms = round((time.monotonic() - start) * 1000, 1)

    text = response.choices[0].message.content or ""
    usage = response.usage

    return {
        "text": text,
        "latency_ms": latency_ms,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "model": response.model,
    }


def generate_chat(
    messages: list[dict],
    model: str,
    max_completion_tokens: int = 1024,
    system: str | None = None,
) -> dict:
    """
    Multi-turn generation. Caller maintains and passes full messages list.
    Same return shape as generate().
    """
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    client = _get_client()

    kwargs = {
        "model": model,
        "messages": full_messages,
        "max_completion_tokens": max_completion_tokens,
        "reasoning_effort": "none",
    }

    start = time.monotonic()
    response = client.chat.completions.create(**kwargs)
    latency_ms = round((time.monotonic() - start) * 1000, 1)

    text = response.choices[0].message.content or ""
    usage = response.usage

    return {
        "text": text,
        "latency_ms": latency_ms,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "model": response.model,
    }
