import os
import json
import requests
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# ---------------------------------------------------------------------------------
# Tool definition for the model
# 'strict': True ensures the model's generated arguments match this schema exactly
# ---------------------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_pokemon_data",
            "description": "Fetch data about a Pokémon from PokeAPI. Returns name, types, abilities, stats, and up to 10 moves.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "pokemon_name": {
                        "type": "string",
                        "description": "The name or ID of the Pokémon, e.g. 'pikachu' or '25'."
                    }
                },
                "required": ["pokemon_name"],
                "additionalProperties": False
            }
        }
    }
]

# ----------------------------------------------------------------------
# Actual implementation of the tool – called when the model requests it
# Returns a compact JSON string containing key Pokémon info
# ----------------------------------------------------------------------
def get_pokemon_data(pokemon_name: str) -> str:
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return json.dumps({"error": f"Could not retrieve data for '{pokemon_name}'"})
        data = resp.json()
        # Extract only essential fields to keep token usage low
        info = {
            "name": data.get("name"),
            "id": data.get("id"),
            "types": [t["type"]["name"] for t in data.get("types", [])],
            "abilities": [a["ability"]["name"] for a in data.get("abilities", [])],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])},
            "moves": [m["move"]["name"] for m in data.get("moves", [])[:10]]  # first 10 moves only
        }
        return json.dumps(info)
    except Exception as e:
        return json.dumps({"error": f"Request failed: {str(e)}"})


# --------------------------------------------------------------------------
# Core interaction loop using tool calling
# The model may call the tool zero, one, or multiple times before answering
# We accumulate tokens across all API calls within this single user turn
# --------------------------------------------------------------------------
def ask_cerebras(prompt: str, model="gpt-oss-120b", max_tokens: int = 150, temperature: float = 0.7):
    total_tokens_used = 0
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Pokémon expert assistant. When the user asks about a Pokémon "
                "(weaknesses, counters, types, moves, evolutions, etc.), use the get_pokemon_data "
                "tool to retrieve its data, then provide a concise, accurate answer based on that data."
            )
        },
        {"role": "user", "content": prompt}
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        total_tokens_used += response.usage.total_tokens
        msg = response.choices[0].message

        # No tool_calls means the model has produced its final answer
        if not msg.tool_calls:
            return msg.content, total_tokens_used

        # Otherwise, append the model's request (with tool_calls) to the conversation
        messages.append(msg.model_dump())
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            if func_name == "get_pokemon_data":
                args = json.loads(tool_call.function.arguments)
                result = get_pokemon_data(args["pokemon_name"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            # Additional tools could be handled here with elif

# -------------------------------------------------------------------
# Main chat loop – runs until user quits or daily token limit is hit
# -------------------------------------------------------------------
def main() -> None:
    total_tokens = 0
    DAILY_LIMIT = 1_000_000

    print("Cerebras Pokémon Expert (type 'quit' to exit)")
    print("Model: llama3.1-8b | Max tokens per answer: 150")
    print("You can ask about weaknesses, types, counters, moves, evolutions, etc.")
    print("-" * 50)

    while total_tokens < DAILY_LIMIT:
        question = input("\nYou: ").strip()
        if question.lower() == 'quit':
            break

        try:
            answer_text, used = ask_cerebras(question)
            print(f"Bot: {answer_text}")

            total_tokens += used
            print(f"[Tokens used: {used}, Total today: {total_tokens:,}]")
        except Exception as e:
            # Distinguish rate/limit errors from other failures
            if "429" in str(e):
                print("Daily limit or rate limit exceeded. Stopping.")
                break
            else:
                print(f"Error: {e}")
                break

    print("\nGoodbye! Total tokens used:", f"{total_tokens:,}")

if __name__ == "__main__":
    main()

