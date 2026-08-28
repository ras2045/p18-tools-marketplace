---
name: ollama-compare
description: Run the same prompt through a local Ollama model and through Claude, and show both real answers side by side. Use when the user wants to compare a local model's answer against Claude's own on one prompt.
argument-hint: "[--model NAME] <prompt>"
disable-model-invocation: true
---

Requires a local Ollama instance at `http://127.0.0.1:11434`.

Step 1 — get the local model's real answer:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ollama_ask.py" $ARGUMENTS`
```

Step 2 — write your own answer to the same prompt (the text after any
`--model NAME` flag), independently, without looking at or being anchored
by the local model's output above.

Step 3 — present both under clear headers, e.g.:

```
## Local (llama3.1:8b)
<the script's real response text, verbatim>

## Claude
<your own independent answer>
```

Do not edit, summarize, or "correct" the local model's response — show it
verbatim. Do not claim one answer is more accurate than the other unless
the user asks you to judge them, and if asked, judge on stated criteria
(e.g. factual accuracy you can actually verify) rather than a vague
quality impression.
