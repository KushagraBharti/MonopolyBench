from typing import Any


def validate_route(payload: dict[str, Any], response: dict[str, Any]) -> None:
    if response.get("model") != payload["model"]:
        raise ValueError(f"Wrong returned model: {response.get('model')}")
    aliases = {"Anthropic": "anthropic", "OpenAI": "openai", "Google AI Studio": "google-ai-studio", "xAI": "xai"}
    returned = response.get("provider")
    provider = aliases.get(str(returned), str(returned))
    allowed = payload.get("provider", {}).get("only", [])
    if provider not in allowed:
        raise ValueError(f"Wrong returned provider: {returned}")
