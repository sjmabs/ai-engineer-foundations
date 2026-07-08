from dotenv import load_dotenv
import os
from toolkit.llm.client import AnthropicClient


load_dotenv()

new_client = AnthropicClient(api_key=os.environ['ANTHROPIC_API_KEY'], model="claude-sonnet-4-6")
print(new_client.complete("You are a helpful F1 race assistant",
                          "Who qualified on pole this week at the F1 Austrian GP?"))

