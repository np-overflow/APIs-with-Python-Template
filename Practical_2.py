import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# TODO 1: Load .env file and assign the API key to Cerebras using OS library

client = Cerebras(
    api_key=
)


def ask_cerebras(prompt: str, model: str = "gpt-oss-120b", max_tokens: int = 150, temperature: float = 0.7) -> dict[str,str]:
    response = client.chat.completions.create(
        # TODO 2: Field in the arguments and the prompt for the Cerebras API
    )
    # TODO 3: Convert the AI's response message to a JSON string

    # TODO 4: Parse the JSON string into a Python dictionary to easily access the 'content' field
    # TODO  : json.loads(answer_json_str)

    return answer_dict


print("Cerebras API Assistant (type 'quit' to exit)")
print("Model: gpt-oss-120b | Max tokens per answer: 150 | Word Length Limit: 8192")
print("-" * 50)

question = input("\nYou: ").strip()

try:
    # TODO 5: Use the function ask_cerebras() and print the Bot's reply out
    # TODO:   print example: "Bot: Hello I am a AI bot"

except Exception as e:
    if "429" in str(e):
        print("Daily limit or rate limit exceeded. Stopping.")
    else:
        print(f"Error: {e}")

print("\nGoodbye!")
