from anthropic import Anthropic, APIError
from anthropic.types import MessageParam
from dotenv import load_dotenv


load_dotenv()

class AnthropicClient:
    """
        Thin wrapper around the Anthropic SDK.
        Handles parameter construction, optional temperature, and API error handling.
    """
    def __init__(self, model: str, temperature: float | None = None):
        self.client = Anthropic()
        self.temperature = temperature
        self.model = model

    def _build_message_params(self, system_prompt: str, messages: list[MessageParam]) -> dict:
        params = {
            "max_tokens": 1024,
            "model": self.model,
            "system": system_prompt,
            "messages": messages
            }
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return params


    def _execute(self, params: dict) -> str:
        try:
            message = self.client.messages.create(**params)
            return message.content[0].text
        except APIError as e:
            raise RuntimeError(f"Anthropic API call failed: {e}") from e


    def complete(self, system_prompt: str, user_message: str) -> str:
        """
        Sends a single uer message to the model and returns the text response.
        """
        messages = [MessageParam(content=user_message, role="user")]
        params = self._build_message_params(system_prompt, messages)
        return self._execute(params)



    def complete_with_history(self, system_prompt: str, messages: list[MessageParam]) -> str:
        """
        Sends a full conversation with message history and return the model's response as a string.
        Caller responsible for constructing and maintaining the messages list.
        """
        params = self._build_message_params(system_prompt, messages)
        return self._execute(params)


new_client = AnthropicClient(model="claude-sonnet-4-6")
print(new_client.complete("You are a helpful F1 race assistant", "Who qualified on pole this week at the F1 Austrian GP?"))