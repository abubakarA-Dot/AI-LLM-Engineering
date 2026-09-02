# """
# Week 1 deliverable: a CLI tool that calls a local Ollama model through its
# OpenAI-compatible endpoint, asks it a free-text question, and forces a
# structured JSON answer back via a tool schema (not just prose).

# Swappable later: change OLLAMA_BASE_URL / OLLAMA_CHAT_MODEL (or point base_url
# at Anthropic/OpenAI once upgraded) without touching the request logic below.
# """

# import argparse
# import json
# from datetime import datetime, timezone
# from pathlib import Path

from ollama import Client
import os
from dotenv import load_dotenv
# from openai import OpenAI

load_dotenv()

# BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
# MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b")
# LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "usage_log.jsonl"

# # Forces the model to answer through this schema instead of free-form prose.
# ANSWER_TOOL = {
#     "type": "function",
#     "function": {
#         "name": "answer_question",
#         "description": "Return a structured answer to the user's question.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "answer": {"type": "string", "description": "The answer, in plain language."},
#                 "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
#             },
#             "required": ["answer", "confidence"],
#         },
#     },
# }

# REQUIRED_KEYS = {"answer", "confidence"}


# def ask(question: str) -> dict:
#     """Calls the model, validates the tool-call arguments actually match our schema, and
#     retries once with a stricter instruction if the model invented its own argument names
#     instead -- observed in practice on qwen2.5:7b, which fires the right function name but
#     doesn't always respect the declared parameters. Raises if it still doesn't comply."""
#     client = OpenAI(base_url=BASE_URL, api_key="ollama")  # api_key is required by the SDK, unused by Ollama locally

#     messages = [{"role": "user", "content": question}]
#     for attempt in range(3):
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=messages,
#             tools=[ANSWER_TOOL],
#             tool_choice={"type": "function", "function": {"name": "answer_question"}},
#         )
#         print("\n Response:", response)
#         tool_call = response.choices[0].message.tool_calls[0]
#         structured = json.loads(tool_call.function.arguments)
#         log_usage(question, response.usage, valid=REQUIRED_KEYS.issubset(structured))

#         if REQUIRED_KEYS.issubset(structured):
#             return structured

#         messages.append({
#             "role": "user",
#             "content": (
#                 f"Your last response used the keys {list(structured.keys())}, "
#                 f"but the schema requires exactly: answer (string), confidence (high/medium/low). "
#                 f"Call answer_question again using exactly those two argument names."
#             ),
#         })

#     raise ValueError(
#         f"Model did not return the required keys {REQUIRED_KEYS} after 2 attempts -- "
#         f"last response: {structured}. This is a real model-capability limit, not a bug -- "
#         f"log it as a Week 5 eval finding."
#     )


# def log_usage(question: str, usage, valid: bool) -> None:
#     LOG_PATH.parent.mkdir(exist_ok=True)
#     entry = {
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#         "model": MODEL,
#         "question": question,
#         "schema_valid": valid,
#         "prompt_tokens": usage.prompt_tokens,
#         "completion_tokens": usage.completion_tokens,
#         "total_tokens": usage.total_tokens,
#     }
#     with LOG_PATH.open("a", encoding="utf-8") as f:
#         f.write(json.dumps(entry) + "\n")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Ask the local LLM a question, get a structured answer back.")
#     parser.add_argument("question", nargs="?", help="The question to ask. Omit to be prompted interactively.")
#     args = parser.parse_args()

#     question = args.question or input("Question: ")
#     result = ask(question)

#     print(json.dumps(result, indent=2))
#     print(f"\n(usage logged to {LOG_PATH})")


# from ollama import chat
# from ollama import ChatResponse

# response = chat(model='qwen2.5:7b', messages=[
#   {
#     'role': 'user',
#     'content': 'What model are you using. just name the model and nothing else. ',
#   }
# ], stream= True,)
# for chunk in response:
#     print(chunk['message']['content'], end='', flush=True)
#     if chunk.total_duration is not None:
#         print(f"\n{round(chunk.total_duration * 1e-9, 1)} seconds")


# import tiktoken
# enc = tiktoken.encoding_for_model("gpt-4")

# client = Client()

# messages = [
#   {
#     'role': 'user',
#     'content': 'What is ollama? just name the model and nothing else. ',
#   },
# ]

# for part in client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
#     print(part.message.content, end='', flush=True)
#     if part.total_duration is not None:
#         print(f"\n{round(part.total_duration * 1e-9, 1)} seconds")

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"

client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)

messages = [
  {
    'role': 'user',
    'content': 'Write abc in 3 different languages. just name the model and nothing else.',
  },
]

for part in client.chat('gpt-oss:120b-cloud', messages=messages, stream=True):
  print(part.message.content, end='', flush=True)
  if part.total_duration is not None:

    print(f"\n{GREEN}{round(part.total_duration * 1e-9, 1)} seconds{RESET}")
    print(f"{BLUE}\033[1m{round(part.total_duration * 1e-9, 1)} seconds{RESET}") 