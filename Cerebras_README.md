# Workshop 2: APIs with Python (Cerebras)

## Table of Contents

- [Resources](#resources)
- [Free Tier Limits](#free-tier-limits)
- [Available Models](#available-models)
- [Common Request Parameters](#common-request-parameters)
- [Feature Matrix – Model Support](#feature-matrix--model-support)
- [Setup](#setup)
- [Feature Examples](#feature-examples)
  - [Streaming](#streaming)
  - [Reasoning](#reasoning)
  - [Predicted Outputs](#predicted-outputs)
  - [Structured Outputs](#structured-outputs)
  - [Tool Calling](#tool-calling)
  - [Prompt Caching](#prompt-caching)
  - [Payload Optimization](#payload-optimization)
  - [CePO](#cepo-cerebras-planning--optimization)
- [Tracking Daily Token Usage](#tracking-daily-token-usage)
- [Common Error Handling](#common-error-handling)

## Resources

- API Key & Platform: [cloud.cerebras.ai](https://cloud.cerebras.ai)  
- Full documentation: [inference-docs.cerebras.ai/introduction](https://inference-docs.cerebras.ai/introduction)  
- Documentation index (all pages): [inference-docs.cerebras.ai/llms.txt](https://inference-docs.cerebras.ai/llms.txt)

| Limit                      | Value                                    |
|----------------------------|------------------------------------------|
| Tokens per day             | `1,000,000` (prompt + completion)        |
| Requests per minute        | Approximately 30 (watch for 429 errors)  |
| Context length (free tier) | Typically 8,192 tokens                   |
| Reset time                 | Midnight UTC                             |
| Credit card required       | No                                       |

All tokens used = prompt and completion which count toward the daily limit.

## Available Models (Free Tier)

| Model ID                         | Description                                        | Typical Use Cases                                                       |
|----------------------------------|----------------------------------------------------|-------------------------------------------------------------------------|
| `llama3.1-8b`                    | Meta Llama 3.1 8B - fast, lightweight              | General chat, simple Q&A, quick prototyping                             |
| `gpt-oss-120b`                   | OpenAI GPT-OSS 120B - powerful generalist          | Complex reasoning, code generation, tool calling, structured outputs    |
| `zai-glm-4.7`                    | Z.ai GLM-4.7 - advanced reasoning, Chinese support | Multilingual tasks, logical puzzles, step‑by‑step reasoning             |
| `qwen-3-235b-a22b-instruct-2507` | Qwen 3 235B - strong in coding and math            | Long‑context understanding, advanced code analysis, mathematical proofs |

The workshop uses `llama3.1-8b` by default to save quota. Swap to other models only when needed.

## Common Request Parameters

Every `chat.completions.create()` call uses these parameters:

| Parameter     | Type / Example                                                                 | Description                                                    |
|---------------|--------------------------------------------------------------------------------|----------------------------------------------------------------|
| `model`       | `"llama3.1-8b"`, `"gpt-oss-120b"`, …                                           | The model to use.                                              |
| `messages`    | `[{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]`   | The conversation history.                                      |
| `temperature` | float, `0.0` to `2.0` (default `1.0`)                                          | Randomness control. 0 = deterministic, higher = more creative. |
| `max_tokens`  | integer, e.g. `150`                                                            | Maximum tokens the model generates. Always set this.           |

**Workshop recommendation:** `max_tokens=150`, `temperature=0.7` for general tasks.

## Feature Matrix – Model Support

| Feature              | llama3.1-8b  | gpt-oss-120b          | zai-glm-4.7           | qwen-3-235b         |
|----------------------|--------------|-----------------------|-----------------------|---------------------|
| Streaming            | ✅            | ✅                     | ✅                     | ✅                   |
| Structured Outputs   | ✅            | ✅                     | ✅                     | ✅                   |
| Tool Calling         | ✅            | ✅                     | ✅                     | ✅                   |
| Reasoning            | ❌            | ✅ (parsed/raw/hidden) | ✅ (parsed/raw/hidden) | ✅ (raw format only) |
| Predicted Outputs    | ❌            | ✅                     | ✅                     | ❌                   |
| Prompt Caching       | ✅            | ✅                     | ✅                     | ✅                   |
| Payload Optimization | ✅            | ✅                     | ✅                     | ✅                   |
| CePO (OptiLLM)       | ✅ (special)  | ❌                     | ❌                     | ❌                   |

## Setup (Every Example Starts Here)

Rename [.env.example](.env.example) with `.env` and put in your API key:

```dotenv
CEREBRAS_API_KEY=your-api-key-here
```

Then in every script:

```python
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
```

## Feature Examples

### **Streaming**

Receive tokens as they are generated, ideal for real‑time display.

**Supported models:** all  
**Key argument:** `stream=True`  
**Use cases:** chatbots, live coding assistants, interactive experiences.

```python
stream = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[{"role": "user", "content": "Explain what a black hole is in three sentences."}],
    max_tokens=150,
    temperature=0.7,
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
```

### Reasoning

The model generates hidden reasoning tokens before the final answer, improving multi‑step problem solving.

**Supported models:** `gpt-oss-120b`, `zai-glm-4.7`, `qwen-3-235b` (raw format)  
**Key arguments:** `reasoning_format` (options: `"parsed"`, `"raw"`, `"hidden"`), model‑specific `reasoning_effort`.  
**Use cases:** math, logic puzzles, complex code analysis.

**Example: GPT-OSS with raw reasoning**

```python
response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[{"role": "user", "content": "If a train leaves at 9 AM traveling 60 mph and another leaves at 10 AM traveling 80 mph, when do they meet?"}],
    reasoning_effort="medium",
    reasoning_format="raw",
    max_tokens=300,
    temperature=0.7,
)
print(response.choices[0].message.content)
```

**Example: GLM with parsed reasoning**

```python
response = client.chat.completions.create(
    model="zai-glm-4.7",
    messages=[{"role": "user", "content": "What is 25 * 4?"}],
    reasoning_format="parsed",
    max_tokens=200,
)
if response.choices[0].message.reasoning:
    print("REASONING:", response.choices[0].message.reasoning)
print("ANSWER:", response.choices[0].message.content)
```

**Disabling reasoning on GLM:**

```python
response = client.chat.completions.create(
    model="zai-glm-4.7",
    messages=[{"role": "user", "content": "Summarize the history of France in one paragraph."}],
    reasoning_effort="none",
    max_tokens=200,
)
```

### Predicted Outputs

Provide a draft of the expected answer. The model reuses matching tokens and regenerates only differences.

**Supported models:** `gpt-oss-120b`, `zai-glm-4.7`  
**Key arguments:** `prediction={"type": "content", "content": "your draft"}`, `temperature=0` recommended.  
**Use cases:** code refactoring, document editing, template filling.

```python
original_code = "body { color: #00FF00; font-size: 16px; }"
instructions = "Change the text color to blue. Return only CSS code."

response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "user", "content": instructions},
        {"role": "user", "content": original_code},
    ],
    prediction={"type": "content", "content": original_code},
    temperature=0,
    max_tokens=200,
)

print(response.choices[0].message.content)

accepted = response.usage.completion_tokens_details.accepted_prediction_tokens
rejected = response.usage.completion_tokens_details.rejected_prediction_tokens
print(f"Accepted: {accepted}, Rejected: {rejected}")
```

### Structured Outputs (JSON Schema)

Force the model to respond with exactly the JSON structure you define. Use `strict=True` for guaranteed schema compliance.

**Supported models:** all  
**Key arguments:** `response_format={"type": "json_schema", "json_schema": { "name": "…", "strict": True, "schema": {…} }}`  
**Use cases:** data extraction, API responses, typed data pipelines.

```python
import json

person_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "city": {"type": "string"}
    },
    "required": ["name", "age"],
    "additionalProperties": False
}

response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You extract person information into JSON."},
        {"role": "user", "content": "Alice is 30 years old and lives in New York."}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": person_schema
        }
    },
    max_tokens=150,
    temperature=0,
)

data = json.loads(response.choices[0].message.content)
print(data)
# Output: {'name': 'Alice', 'age': 30, 'city': 'New York'}
```

**JSON mode** (no schema, just valid JSON):

```python
response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[
        {"role": "system", "content": "Respond with JSON."},
        {"role": "user", "content": "List three colors."}
    ],
    response_format={"type": "json_object"},
    max_tokens=100,
)
print(response.choices[0].message.content)
```

### Tool Calling

Let the model request external tools (APIs, databases, calculators) and use the results.

**Supported models:** all  
**Key arguments:** `tools=[ {...} ]`, `tool_choice` (optional), `parallel_tool_calls=True/False`. Each tool can set `strict=True` for argument validation.  
**Use cases:** agents, real‑time data retrieval, multi‑step workflows.

**Calculator example with multi-turn:**

```python
import json

def calculate(expression):
    sanitized = expression.replace(" ", "")
    try:
        result = eval(sanitized)
        return str(result)
    except Exception:
        return "Error"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "strict": True,
            "description": "Evaluate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The expression to evaluate, e.g. '15*7'"
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    }
]

messages = [
    {"role": "system", "content": "You are a helpful assistant with a calculator tool."},
    {"role": "user", "content": "First multiply 15 by 7. Then add 20 to that result and divide by 2."}
]

available_functions = {"calculate": calculate}

while True:
    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=messages,
        tools=tools,
        parallel_tool_calls=False,
        max_tokens=200,
    )
    msg = response.choices[0].message

    if not msg.tool_calls:
        print("Assistant:", msg.content)
        break

    messages.append(msg.model_dump())

    for call in msg.tool_calls:
        func_name = call.function.name
        args = json.loads(call.function.arguments)
        result = available_functions[func_name](**args)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(result),
        })
```

**Parallel tool calling (weather comparison):**

```python
def get_weather(location):
    data = {"Paris": 18, "Berlin": 15, "London": 14}
    return json.dumps({"location": location, "temperature": data.get(location, 20)})

tools_weather = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "strict": True,
            "description": "Get current temperature for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"],
                "additionalProperties": False
            }
        }
    }
]

messages = [
    {"role": "user", "content": "Which is warmer: Paris or Berlin?"}
]

response = client.chat.completions.create(
    model="zai-glm-4.7",
    messages=messages,
    tools=tools_weather,
    parallel_tool_calls=True,
    max_tokens=200,
)

msg = response.choices[0].message
if msg.tool_calls:
    messages.append(msg)
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        result = get_weather(args["location"])
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    final_response = client.chat.completions.create(
        model="zai-glm-4.7",
        messages=messages,
    )
    print("Final answer:", final_response.choices[0].message.content)
```

### Prompt Caching

Automatically reuses previously computed prompt prefixes to reduce time‑to‑first‑token. No code changes required; optional `prompt_cache_key` improves cache hits.

**Supported models:** all  
**Key arguments:** none required. Use `prompt_cache_key="session-id"` to group related requests.  
**Use cases:** multi‑turn conversations, large static system prompts, few‑shot examples.  
**Track cache hits:** `response.usage.prompt_tokens_details.cached_tokens`

```python
# First turn: creates cache
resp1 = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "What is a variable?"}
    ],
    prompt_cache_key="chat-session-1",
    max_tokens=100,
)

# Second turn: same system prompt, will hit cache
resp2 = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Show me an example in Python."}
    ],
    prompt_cache_key="chat-session-1",
    max_tokens=100,
)

cached = resp2.usage.prompt_tokens_details.cached_tokens
print(f"Cached tokens: {cached}")
```

**Structure for optimal caching:** keep static content (system message, tool definitions) at the beginning of the `messages` array, and dynamic content (user question) at the end.

### Payload Optimization

Compress the request body with gzip and/or msgpack to reduce network transfer time for large prompts. Requires `requests` instead of the high‑level SDK.

**Supported models:** all (on `/v1/chat/completions`)  
**Key arguments:** HTTP headers `Content-Type` and `Content-Encoding`.  
**Use cases:** long conversations, many tool definitions, batch processing.

**Gzip compression only:**

```python
import requests, json, gzip, os

api_key = os.getenv("CEREBRAS_API_KEY")
payload = {
    "model": "llama3.1-8b",
    "messages": [{"role": "user", "content": "Explain quantum computing in one paragraph."}],
    "max_tokens": 150,
    "temperature": 0.7,
}
compressed_body = gzip.compress(json.dumps(payload).encode("utf-8"), compresslevel=5)

response = requests.post(
    "https://api.cerebras.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Content-Encoding": "gzip",
    },
    data=compressed_body,
)
print(response.json()["choices"][0]["message"]["content"])
```

**msgpack + gzip (maximum compression):**

```python
import requests, msgpack, gzip, os

api_key = os.getenv("CEREBRAS_API_KEY")
payload = {
    "model": "llama3.1-8b",
    "messages": [{"role": "user", "content": "Explain quantum computing in one paragraph."}],
    "max_tokens": 150,
}
packed = msgpack.packb(payload)
compressed = gzip.compress(packed, compresslevel=5)

response = requests.post(
    "https://api.cerebras.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/vnd.msgpack",
        "Content-Encoding": "gzip",
    },
    data=compressed,
)
print(response.json()["choices"][0]["message"]["content"])
```

### CePO: Cerebras Planning & Optimization

A research framework that wraps `llama3.1-8b` with multi‑step planning and Best‑of‑N to improve reasoning at inference time.

**Supported model:** `llama3.1-8b`  
**Required packages:** `optillm`, `cerebras_cloud_sdk`  
**Usage:** via command line.

```bash
pip install --upgrade cerebras_cloud_sdk optillm
export CEREBRAS_API_KEY=your-api-key-here
optillm --base-url https://api.cerebras.ai --approach cepo
```

Optionally print intermediate steps:

```bash
optillm --base-url https://api.cerebras.ai --approach cepo --cepo_print_output true
```

## Tracking Daily Token Usage

The free tier limit is 1,000,000 tokens per day. Track usage with `response.usage.total_tokens`. 

To persist across script runs, use a file:

```python
import json
from datetime import date

TOKEN_FILE = "token_usage.json"
DAILY_LIMIT = 1000000

def load_usage():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") == str(date.today()):
            return data.get("tokens_used", 0)
    return 0

def save_usage(used):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"date": str(date.today()), "tokens_used": used}, f)

total_tokens = load_usage()

def ask(prompt, model="llama3.1-8b", max_tokens=150):
    global total_tokens
    if total_tokens >= DAILY_LIMIT:
        raise Exception("Daily token limit reached.")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    total_tokens += response.usage.total_tokens
    save_usage(total_tokens)
    print(f"Tokens used this call: {response.usage.total_tokens} | Total today: {total_tokens}")
    return response.choices[0].message.content

answer = ask("What is the capital of France?")
print(answer)
```

## Common Error Handling

**HTTP 429 (rate or quota exceeded):**

```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    if "429" in str(e):
        print("Daily limit or rate limit hit. Try again later.")
    else:
        print(f"Other error: {e}")
```

**Daily limit reached:** wait until midnight UTC.  
**Rate limit per minute:** add `time.sleep(2)` between requests.