# Ollama Local LLM Tools — Claude Code Plugin

Three real, tested commands for working with a local Ollama instance from
inside Claude Code.

## What's real here

- **`/ollama-tools:ollama-ask`** — sends a prompt to a local Ollama model
  (default `llama3.1:8b`) via `/api/generate` and prints its real response,
  real token count, and real elapsed time.
- **`/ollama-tools:ollama-embed`** — embeds text with `nomic-embed-text`
  via `/api/embed` and prints the real dimension count (768), real L2
  norm, and first 8 real vector values.
- **`/ollama-tools:ollama-compare`** — runs one prompt through both the
  local model and Claude, and shows both real, independently-generated
  answers side by side without editing either.

All three were tested live against a running Ollama instance
(`llama3.1:8b`, `llama3.3:70b`, `llama3.1:8b-instruct-fp16`,
`nomic-embed-text`) before being packaged, including the error path for a
model name that doesn't exist.

## Requirements

- Python 3 on PATH (standard library only — no pip dependencies)
- A local Ollama instance at `http://127.0.0.1:11434`
  (https://ollama.com) with at least one completion model pulled for
  `ollama-ask`/`ollama-compare`, and `nomic-embed-text` pulled for
  `ollama-embed`

## Install

Test without installing:
```
claude --plugin-dir /path/to/ollama-tools-plugin
```

Install for yourself, in every project:
```
claude plugin install /path/to/ollama-tools-plugin --scope user
```

Or via a marketplace:
```
/plugin marketplace add ras2045/p18-tools-marketplace
/plugin install ollama-tools@p18-marketplace
```

## Structure

```
ollama-tools-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── ollama-ask/SKILL.md
│   ├── ollama-embed/SKILL.md
│   └── ollama-compare/SKILL.md
└── scripts/
    ├── ollama_ask.py       # entry point for ollama-ask and ollama-compare
    └── ollama_embed.py     # entry point for ollama-embed
```

All three skills are `disable-model-invocation: true` — user-triggered
slash commands only, Claude won't invoke them automatically mid-conversation.
