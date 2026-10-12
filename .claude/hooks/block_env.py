"""PreToolUse hook: stop Claude Code from reading .env (your secrets).

Claude Code pipes the proposed tool call to this script as JSON on stdin.
Exit 0 = allow. Exit 2 = block, and whatever is printed to stderr is shown
to Claude so it knows why.
"""
import json
import sys

payload = json.load(sys.stdin)
file_path = (payload.get("tool_input") or {}).get("file_path", "")

# Block the real secrets file, but allow the committed .env.example template.
if ".env" in file_path and ".env.example" not in file_path:
    print(
        "Blocked: .env holds secrets (e.g. OPENAI_API_KEY) and must not be read.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
