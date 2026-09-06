"""
Week 1 deliverable: a CLI tool that calls a local Ollama model through its
OpenAI-compatible endpoint, asks it a free-text question, and forces a
structured JSON answer back via a tool schema (not just prose).

Swappable later: change OLLAMA_BASE_URL / OLLAMA_CHAT_MODEL in .env (or point
base_url at Anthropic/OpenAI once upgraded) without touching the request logic
below -- that portability is the whole point of using the openai-compatible
client instead of Ollama's own native client.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b")
LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "usage_log.jsonl"

REQUIRED_KEYS = {"answer", "confidence"}

# Forces the model to answer through this schema instead of free-form prose.
ANSWER_TOOL = {
    "type": "function",
    "function": {
        "name": "answer_question",
        "description": "Return a structured answer to the user's question.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The answer, in plain language."},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            },
            "required": ["answer", "confidence"],
        },
    },
}


def ask(question: str) -> dict:
    """Calls the model, validates the tool-call arguments actually match our schema, and
    retries once with a stricter instruction if the model didn't comply -- either by inventing
    its own argument names, or (observed in practice, even with tool_choice forced) by not
    calling the tool at all and just answering in plain content instead. Raises if it still
    doesn't comply after a retry."""
    client = OpenAI(base_url=BASE_URL, api_key="ollama")  # api_key is required by the SDK, unused by Ollama locally

    messages = [{"role": "user", "content": question}]
    structured = None
    for attempt in range(2):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[ANSWER_TOOL],
            tool_choice={"type": "function", "function": {"name": "answer_question"}},
        )
        message = response.choices[0].message

        if not message.tool_calls:
            # tool_choice doesn't guarantee compliance -- the model sometimes just answers
            # in plain content instead. Treat that as invalid, not a crash.
            structured = {"_raw_content": message.content}
            valid = False
        else:
            tool_call = message.tool_calls[0]
            structured = json.loads(tool_call.function.arguments)
            valid = REQUIRED_KEYS.issubset(structured)

        log_usage(question, response.usage, valid=valid)

        if valid:
            return structured

        messages.append({
            "role": "user",
            "content": (
                f"Your last response used the keys {list(structured.keys())}, "
                f"but the schema requires exactly: answer (string), confidence (high/medium/low). "
                f"Call answer_question again using exactly those two argument names."
            ),
        })

    raise ValueError(
        f"Model did not return the required keys {REQUIRED_KEYS} after 2 attempts -- "
        f"last response: {structured}. This is a real model-capability limit, not a bug -- "
        f"log it as a Week 5 eval finding."
    )


def log_usage(question: str, usage, valid: bool) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "question": question,
        "schema_valid": valid,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask the local LLM a question, get a structured answer back.")
    parser.add_argument("question", nargs="?", help="The question to ask. Omit to be prompted interactively.")
    args = parser.parse_args()

    question = args.question or input("Question: ")
    try:
        result = ask(question)
        print(f"{GREEN}{json.dumps(result, indent=2)}{RESET}")
    except ValueError as e:
        print(f"{RED}{e}{RESET}")

    print(f"\n(usage logged to {LOG_PATH})")
