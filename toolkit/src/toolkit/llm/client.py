from typing import Any

from anthropic import Anthropic, APIError
from anthropic.types import MessageParam


class AnthropicClient:
    """
        Thin wrapper around the Anthropic SDK.
        Handles parameter construction, optional temperature, and API error handling.
    """
    def __init__(self, api_key: str, model: str):
        self._client = Anthropic(api_key=api_key)
        self.model = model

    def _build_message_params(self, system_prompt: str, messages: list[MessageParam], max_tokens: int, temperature: float | None) -> dict[str, Any]:
        params = {
            "max_tokens": max_tokens,
            "model": self.model,
            "system": system_prompt,
            "messages": messages
            }
        if temperature is not None:
            params["temperature"] = temperature
        return params


    def _execute(self, params: dict[str, Any]) -> str:
        try:
            message = self._client.messages.create(**params)
            # TODO: handle non-text content blocks
            return message.content[0].text
        except APIError as e:
            raise RuntimeError(f"Anthropic API call failed: {e}") from e # note: collapses all SDK error types to RuntimeError


    def complete(self, system_prompt: str, user_message: str, max_tokens: int = 1024, temperature: float | None = None) -> str:
        """
        Sends a single user message to the model and returns the text response.
        """
        messages = [MessageParam(content=user_message, role="user")]
        params = self._build_message_params(system_prompt, messages, max_tokens, temperature)
        return self._execute(params)



    def complete_with_history(self, system_prompt: str, messages: list[MessageParam], max_tokens: int = 1024, temperature: float | None = None) -> str:
        """
        Sends a full conversation with message history and returns the model's response as a string.
        Caller responsible for constructing and maintaining the messages list.
        """
        params = self._build_message_params(system_prompt, messages, max_tokens, temperature)
        return self._execute(params)

