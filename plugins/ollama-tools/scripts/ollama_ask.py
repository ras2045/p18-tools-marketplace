#!/usr/bin/env python3
"""Query a local Ollama model. Usage: ollama_ask.py [--model NAME] PROMPT..."""
import json
import sys
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.1:8b"


def list_models():
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
        data = json.load(r)
    return [m["name"] for m in data.get("models", [])]


def ask(model, prompt, timeout=300):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data


def main():
    args = sys.argv[1:]
    model = DEFAULT_MODEL
    if args and args[0] == "--model":
        model = args[1]
        args = args[2:]

    if not args:
        print("Usage: ollama_ask.py [--model NAME] PROMPT...", file=sys.stderr)
        sys.exit(1)
    prompt = " ".join(args)

    try:
        models = list_models()
    except Exception as e:
        print(f"Cannot reach Ollama at {OLLAMA_URL} — is it running? ({e})", file=sys.stderr)
        sys.exit(1)

    if model not in models:
        print(f"Model '{model}' not found. Available: {', '.join(models)}", file=sys.stderr)
        sys.exit(1)

    try:
        result = ask(model, prompt)
    except Exception as e:
        print(f"Request to Ollama failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[{model}] ({result.get('eval_count', '?')} tokens, "
          f"{result.get('total_duration', 0) / 1e9:.1f}s)")
    print()
    print(result.get("response", "").strip())


if __name__ == "__main__":
    main()
