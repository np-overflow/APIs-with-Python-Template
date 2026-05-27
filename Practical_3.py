import os
import json
import requests
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

# Additional Data
# TODO 1: Add your custom API with the specific data included
# TODO:   Add your final output to context_data variable


context_data =


# Cerebras
# TODO 2: From Practical_2.py, Load .env file and assign the API key to Cerebras using OS library

client = Cerebras(
    api_key=
)



def ask_cerebras(prompt: str, model: str = "gpt-oss-120b", max_tokens: int = 150, temperature: float = 0.7) -> dict[str,str]:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. When the user message contains extra "
                    "data (in JSON or list form), use that data to answer the question "
                    "accurately and concisely. If no data is given, answer from your own knowledge."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    # TODO 3: From Practical_2.py, Convert the AI's response message to a JSON string

    # TODO 4: From Practical_2.py, Parse the JSON string into a Python dictionary to easily access the 'content' field

    return answer_dict


print("Cerebras API Assistant (type 'quit' to exit)")
print("Model: llama3.1-8b | Max tokens per answer: 150 | Word Length Limit: 8192")
print("-" * 50)


question = input("\nYou: ").strip()

full_prompt = f"Additional data:\n{context_data}\n\nQuestion: {question}"

try:
    # TODO 5: From Practical_2.py, Use the function ask_cerebras() and print the Bot's reply out
    # TODO:   print example: "Bot: Hello I am a AI bot"


except Exception as e:
    if "429" in str(e):
        print("Daily limit or rate limit exceeded. Stopping.")
    else:
        print(f"Error: {e}")

print("\nGoodbye!")
