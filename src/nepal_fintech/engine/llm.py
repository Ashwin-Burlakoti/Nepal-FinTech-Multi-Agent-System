"""LiteLLM wrapper for structured chat completions."""
from __future__ import annotations

import json

import litellm

from nepal_fintech.config import settings

# Suppress litellm logging noise
litellm.suppress_debug_info = True


async def chat(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    temperature: float = 0.3,
) -> str:
    """Send a chat completion request and return the response content."""
    model = model or settings.llm_model
    response = await litellm.acompletion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    return response.choices[0].message.content or ""


def _clean_json_text(raw: str) -> str:
    """Extract and clean raw JSON text by stripping markdown code blocks."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Drop leading ``` or ```json
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1 :]
        else:
            cleaned = cleaned[3:]
    cleaned = cleaned.removesuffix("```")
    cleaned = cleaned.strip()

    # If surrounded by extraneous text, extract bracketed JSON object
    if not (cleaned.startswith("{") and cleaned.endswith("}")):
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx : end_idx + 1]

    return cleaned


async def chat_json(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    temperature: float = 0.2,
) -> dict:
    """Chat completion that parses the response as JSON."""
    # Append JSON instruction to system prompt
    full_system = (
        system_prompt
        + "\n\nYou MUST respond with valid JSON only. No markdown fences."
    )
    raw = await chat(full_system, user_prompt, model, temperature)
    cleaned = _clean_json_text(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        msg = f"Failed to parse LLM response as JSON: {exc}. Content: {raw!r}"
        raise ValueError(msg) from exc
