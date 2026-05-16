from __future__ import annotations

import asyncio
import json
import os
import random
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import httpx


@dataclass(slots=True)
class OpenRouterResult:
    ok: bool
    status_code: int | None
    response_json: dict[str, Any] | None
    error: str | None
    error_type: str | None
    request_id: str | None
    request_payload_raw: str | None = None
    response_text: str | None = None


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_s: float = 30.0,
        max_retries: int = 2,
        extra_headers: dict[str, str] | None = None,
        stream_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._extra_headers = extra_headers or {}
        self._stream_callback = stream_callback
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout_s))
        self._rng = random.Random(0)

    def _backoff_delay(self, attempt: int) -> float:
        base = 0.5
        jitter = self._rng.random() * 0.1
        return base * (2**attempt) + jitter

    async def create_chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        parallel_tool_calls: bool | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        reasoning: dict[str, Any] | None = None,
    ) -> OpenRouterResult:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if parallel_tool_calls is not None:
            payload["parallel_tool_calls"] = parallel_tool_calls
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if reasoning is not None:
            payload["reasoning"] = reasoning
        if self._stream_callback is not None:
            payload["stream"] = True
        payload_text = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)

        if not self._api_key:
            return OpenRouterResult(
                ok=False,
                status_code=None,
                response_json=None,
                error="OPENROUTER_API_KEY not set",
                error_type="no_api_key",
                request_id=None,
                request_payload_raw=payload_text,
                response_text=None,
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            **self._extra_headers,
        }
        url = f"{self._base_url}/chat/completions"
        if self._stream_callback is not None:
            return await self._create_streaming_chat_completion(
                url=url,
                headers=headers,
                payload_text=payload_text,
            )

        last_error: OpenRouterResult | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.post(url, headers=headers, content=payload_text)
                response_text = response.text
                request_id = response.headers.get("x-request-id") or response.headers.get("openrouter-request-id")
                if response.status_code >= 400:
                    status_code = response.status_code
                    if status_code == 429:
                        error_type = "http_429"
                        retryable = True
                    elif 500 <= status_code < 600:
                        error_type = "http_5xx"
                        retryable = True
                    else:
                        error_type = "http_4xx"
                        retryable = False
                    if retryable and attempt < self._max_retries:
                        await asyncio.sleep(self._backoff_delay(attempt))
                        continue
                    error_text = response_text.strip()
                    return OpenRouterResult(
                        ok=False,
                        status_code=status_code,
                        response_json=None,
                        error=error_text or f"HTTP {status_code}",
                        error_type=error_type,
                        request_id=request_id,
                        request_payload_raw=payload_text,
                        response_text=response_text,
                    )
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    return OpenRouterResult(
                        ok=False,
                        status_code=response.status_code,
                        response_json=None,
                        error="Invalid JSON response from OpenRouter",
                        error_type="invalid_json",
                        request_id=request_id,
                        request_payload_raw=payload_text,
                        response_text=response_text,
                    )
                if request_id is None:
                    request_id = data.get("id")
                return OpenRouterResult(
                    ok=True,
                    status_code=response.status_code,
                    response_json=data,
                    error=None,
                    error_type=None,
                    request_id=request_id,
                    request_payload_raw=payload_text,
                    response_text=response_text,
                )
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = OpenRouterResult(
                    ok=False,
                    status_code=None,
                    response_json=None,
                    error=str(exc),
                    error_type="network_error",
                    request_id=None,
                    request_payload_raw=payload_text,
                    response_text=None,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                return last_error

        return last_error or OpenRouterResult(
            ok=False,
            status_code=None,
            response_json=None,
            error="OpenRouter request failed",
            error_type="unknown",
            request_id=None,
            request_payload_raw=payload_text,
            response_text=None,
        )

    async def _create_streaming_chat_completion(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload_text: str,
    ) -> OpenRouterResult:
        last_error: OpenRouterResult | None = None
        for attempt in range(self._max_retries + 1):
            try:
                async with self._client.stream("POST", url, headers=headers, content=payload_text) as response:
                    request_id = response.headers.get("x-request-id") or response.headers.get("openrouter-request-id")
                    if response.status_code >= 400:
                        response_text = await response.aread()
                        text = response_text.decode("utf-8", errors="replace")
                        if response.status_code == 429:
                            error_type = "http_429"
                            retryable = True
                        elif 500 <= response.status_code < 600:
                            error_type = "http_5xx"
                            retryable = True
                        else:
                            error_type = "http_4xx"
                            retryable = False
                        if retryable and attempt < self._max_retries:
                            await asyncio.sleep(self._backoff_delay(attempt))
                            continue
                        return OpenRouterResult(
                            ok=False,
                            status_code=response.status_code,
                            response_json=None,
                            error=text.strip() or f"HTTP {response.status_code}",
                            error_type=error_type,
                            request_id=request_id,
                            request_payload_raw=payload_text,
                            response_text=text,
                        )
                    stream = _StreamingCompletionAccumulator(request_id=request_id)
                    raw_chunks: list[str] = []
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line.removeprefix("data:").strip()
                        if not data:
                            continue
                        if data == "[DONE]":
                            break
                        raw_chunks.append(data)
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        events = stream.apply_chunk(chunk)
                        if not events and chunk.get("choices"):
                            events = [{"type": "raw_delta", "text": json.dumps(chunk.get("choices", [{}])[0].get("delta", {}), ensure_ascii=True)}]
                        for event in events:
                            await self._emit_stream_event(event)
                    response_json = stream.to_response_json()
                    return OpenRouterResult(
                        ok=True,
                        status_code=response.status_code,
                        response_json=response_json,
                        error=None,
                        error_type=None,
                        request_id=request_id or response_json.get("id"),
                        request_payload_raw=payload_text,
                        response_text="\n".join(raw_chunks),
                    )
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                last_error = OpenRouterResult(
                    ok=False,
                    status_code=None,
                    response_json=None,
                    error=str(exc),
                    error_type="network_error",
                    request_id=None,
                    request_payload_raw=payload_text,
                    response_text=None,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                return last_error

        return last_error or OpenRouterResult(
            ok=False,
            status_code=None,
            response_json=None,
            error="OpenRouter streaming request failed",
            error_type="unknown",
            request_id=None,
            request_payload_raw=payload_text,
            response_text=None,
        )

    async def _emit_stream_event(self, event: dict[str, Any]) -> None:
        if self._stream_callback is not None:
            await self._stream_callback(event)

    async def aclose(self) -> None:
        await self._client.aclose()


class _StreamingCompletionAccumulator:
    def __init__(self, *, request_id: str | None) -> None:
        self._id = request_id
        self._model: str | None = None
        self._created: int | None = None
        self._content_parts: list[str] = []
        self._reasoning_parts: list[str] = []
        self._tool_calls: dict[int, dict[str, Any]] = {}
        self._finish_reason: str | None = None

    def apply_chunk(self, chunk: dict[str, Any]) -> list[dict[str, Any]]:
        if self._id is None:
            self._id = chunk.get("id")
        if self._model is None:
            self._model = chunk.get("model")
        if self._created is None:
            self._created = chunk.get("created")
        events: list[dict[str, Any]] = []
        choice = (chunk.get("choices") or [{}])[0]
        delta = choice.get("delta") or {}
        if choice.get("finish_reason") is not None:
            self._finish_reason = choice.get("finish_reason")
        reasoning = delta.get("reasoning") or delta.get("reasoning_content")
        if isinstance(reasoning, str) and reasoning:
            self._reasoning_parts.append(reasoning)
            events.append({"type": "reasoning_delta", "text": reasoning})
        content = delta.get("content")
        if isinstance(content, str) and content:
            self._content_parts.append(content)
            events.append({"type": "content_delta", "text": content})
        for item in delta.get("tool_calls") or []:
            if not isinstance(item, dict):
                continue
            index = int(item.get("index") or 0)
            current = self._tool_calls.setdefault(
                index,
                {
                    "id": item.get("id") or f"tool_call_{index}",
                    "type": item.get("type") or "function",
                    "function": {"name": "", "arguments": ""},
                },
            )
            if item.get("id"):
                current["id"] = item["id"]
            if item.get("type"):
                current["type"] = item["type"]
            function_delta = item.get("function") or {}
            function = current.setdefault("function", {"name": "", "arguments": ""})
            name = function_delta.get("name")
            if isinstance(name, str) and name:
                function["name"] = f"{function.get('name', '')}{name}"
                events.append({"type": "tool_name_delta", "text": name})
            arguments = function_delta.get("arguments")
            if isinstance(arguments, str) and arguments:
                function["arguments"] = f"{function.get('arguments', '')}{arguments}"
                events.append({"type": "tool_arguments_delta", "text": arguments})
        return events

    def to_response_json(self) -> dict[str, Any]:
        message: dict[str, Any] = {
            "role": "assistant",
            "content": "".join(self._content_parts) or None,
        }
        reasoning = "".join(self._reasoning_parts)
        if reasoning:
            message["reasoning"] = reasoning
        if self._tool_calls:
            message["tool_calls"] = [self._tool_calls[index] for index in sorted(self._tool_calls)]
        return {
            "id": self._id,
            "object": "chat.completion",
            "created": self._created,
            "model": self._model,
            "choices": [
                {
                    "index": 0,
                    "message": message,
                    "finish_reason": self._finish_reason,
                }
            ],
        }
