# RAG Assistant for Doroob Workforce-Development Programs

See [PROJECT.md](PROJECT.md) for the full problem statement. This is a 16-week
build toward an AI/LLM engineering portfolio project, following a free-first
(Ollama, local) path with an optional upgrade to Anthropic/OpenAI later.

## Week 1: `llm_client.py`

A CLI tool that asks a local Ollama model a free-text question and forces a
**structured JSON answer** back via a tool schema (`answer` + `confidence`),
instead of unstructured prose.

**Design decision:** built on the `openai` Python package pointed at Ollama's
OpenAI-compatible endpoint (`OLLAMA_BASE_URL` in `.env`), rather than Ollama's
own native client. The whole point of Week 1 is portability -- swapping to
Anthropic/OpenAI later should mean changing `.env`, not rewriting the request
logic. (A native-client version was explored during development but dropped
for this reason -- see git history if curious.)

**Validation + retry:** in testing, `qwen2.5:7b` reliably calls the right tool
(`answer_question`) but doesn't always respect the declared argument names on
the first attempt -- observed real failures returning made-up keys like
`{"question": ..., "context": ...}` instead of `{"answer": ..., "confidence": ...}`.
The script validates the returned keys and retries once with an explicit
correction if they don't match, raising a clear error if it still doesn't
comply after two attempts. Across early testing, roughly 2 of 7 calls needed
the retry -- a real, measured number, not a guess (see `logs/usage_log.jsonl`).

### How to run it

```bash
python src/llm_client.py "your question here"
# or, with no argument, it prompts interactively:
python src/llm_client.py
```

Requires [Ollama](https://ollama.com) running locally with `qwen2.5:7b`
pulled (`ollama pull qwen2.5:7b`), and `.env` set up per `.env.example`.

### Example runs

**Run 1:**
```
$ python src/llm_client.py "What is the capital of Saudi Arabia?"
{
  "answer": "The capital of Saudi Arabia is Riyadh.",
  "confidence": "high"
}
```

**Run 2** (note: this answer is generic/off-target -- `qwen2.5:7b` has no
specific knowledge of Doroob's actual programs like Tamheer, TVTC, or Hafiz,
and defaults to general Vision 2030 talking points instead. This is exactly
the kind of gap Week 3-4's RAG pipeline is meant to fix, by grounding answers
in the project's own document corpus instead of the model's general training):
```
$ python src/llm_client.py "What are the main workforce-development programs in Saudi Arabia?"
{
  "answer": "The main workforce-development programs in Saudi Arabia include the Saudi Vision 2030 initiative, which focuses on diversifying the economy and reducing dependence on oil. The program includes efforts to enhance skills and education, support entrepreneurship, and promote private sector growth. Other notable programs are the National Industrial Development and Logistics Program and the National Manufacturing Development Program, aimed at boosting local industries and manufacturing.",
  "confidence": "high"
}
```

**Run 3:**
```
$ python src/llm_client.py "Is Python a compiled or interpreted language?"
{
  "answer": "Python is generally considered an interpreted language, though it can also be compiled to bytecode that can run on a Python virtual machine.",
  "confidence": "high"
}
```

### Usage log

Every call appends one line to `logs/usage_log.jsonl` (gitignored -- local
only): timestamp, model, question, whether the schema validated on the first
try, and token counts. This is the raw data behind the "2 of 7 needed a
retry" figure above, and will feed into Week 5's eval work.
