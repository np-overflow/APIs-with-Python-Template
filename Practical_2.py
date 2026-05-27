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
# TODO 2: Load .env file and assign the API key to Cerebras using OS library

client = Cerebras(
    api_key=
)


# ====================================
# DO NOT MODIFY THE BELOW SECTION
# ====================================
def ask_cerebras(prompt: str, model="llama3.1-8b", max_tokens: int = 150, temperature: float = 0.7) -> tuple[dict[str,str], int | None] :
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
    answer_json_str = response.choices[0].message.model_dump_json(indent=4)
    answer_dict = json.loads(answer_json_str)
    tokens = response.usage.total_tokens

    return answer_dict, tokens
# ====================================
# DO NOT MODIFY THE ABOVE SECTION
# ====================================


def main() -> None:
    total_tokens = 0
    DAILY_LIMIT = 1_000_000

    print("Cerebras API Assistant (type 'quit' to exit)")
    print("Model: llama3.1-8b | Max tokens per answer: 150 | Word Length Limit: 8192")
    print("-" * 50)

    while total_tokens < DAILY_LIMIT:
        question = input("\nYou: ").strip()
        if question.lower() == 'quit':
            break

        full_prompt = f"Additional data:\n{context_data}\n\nQuestion: {question}"

        try:
            # TODO 3: Use the function ask_cerebras() and print the Bot's reply out


            # TODO 4: From the tokens provided by ask_cerebras(), add it to the total_token variable
            # TODO  : Print out the token used and total token used today

        except Exception as e:
            if "429" in str(e):
                print("Daily limit or rate limit exceeded. Stopping.")
                break
            else:
                print(f"Error: {e}")
                break

    print("\nGoodbye! Total tokens used:", f"{total_tokens:,}")


if __name__ == "__main__":
    main()
