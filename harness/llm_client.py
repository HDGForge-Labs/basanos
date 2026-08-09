"""
Unified LLM client for Basanos-3. Routes generate() calls to the correct
provider client based on provider argument. Returns the same shape as both
underlying clients:
  {text, latency_ms, input_tokens, output_tokens, model}

Supported providers: "anthropic", "openai"
Supported models:
  anthropic: claude-haiku-4-5-20251001
  openai:    gpt-5.6-luna, gpt-5.6-terra

The provider must match the model -- no cross-validation is performed here,
but mismatches will fail at the API level with a clear error.
"""
from harness import anthropic_client
from harness import openai_client

SUPPORTED_PROVIDERS = ("anthropic", "openai")

# Canonical model strings for Basanos-3
MODELS = {
    "luna":  ("openai",    "gpt-5.6-luna"),
    "terra": ("openai",    "gpt-5.6-terra"),
    "haiku": ("anthropic", "claude-haiku-4-5-20251001"),
}


def generate(
    prompt: str,
    provider: str,
    model: str,
    max_tokens: int = 1024,
    system: str | None = None,
) -> dict:
    """
    Single-turn generation routed to the correct provider.

    Args:
        prompt:    User-turn text.
        provider:  "anthropic" or "openai".
        model:     Full model string (e.g. "gpt-5.6-luna").
        max_tokens: Max output tokens (mapped to correct param per provider).
        system:    Optional system prompt.

    Returns:
        {text, latency_ms, input_tokens, output_tokens, model}
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Must be one of {SUPPORTED_PROVIDERS}.")

    if provider == "anthropic":
        return anthropic_client.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            system=system,
        )
    else:  # openai
        return openai_client.generate(
            prompt=prompt,
            model=model,
            max_completion_tokens=max_tokens,
            system=system,
        )


def generate_chat(
    messages: list[dict],
    provider: str,
    model: str,
    max_tokens: int = 1024,
    system: str | None = None,
) -> dict:
    """
    Multi-turn generation routed to the correct provider.
    Caller maintains full messages list across turns.
    """
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Must be one of {SUPPORTED_PROVIDERS}.")

    if provider == "anthropic":
        return anthropic_client.generate_chat(
            messages=messages,
            max_tokens=max_tokens,
            system=system,
        )
    else:  # openai
        return openai_client.generate_chat(
            messages=messages,
            model=model,
            max_completion_tokens=max_tokens,
            system=system,
        )


def resolve_model(slug: str) -> tuple[str, str]:
    """
    Convenience: given a short slug ("luna", "terra", "haiku"),
    returns (provider, model_string).
    """
    if slug not in MODELS:
        raise ValueError(
            f"Unknown model slug '{slug}'. Known slugs: {list(MODELS.keys())}. "
            f"Or pass --provider and --model directly."
        )
    return MODELS[slug]
