#!/usr/bin/env python3
"""
Pretty-print Claude stream-json events from stdin.

Reads newline-delimited JSON produced by `claude --output-format stream-json`
and prints a human-readable summary of assistant messages, tool calls, and the
final result with cost and duration.

Usage:
    tail -f result.json --pid=<claude_pid> | python3 stream-claude-output.py
"""

import json
import signal
import sys

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

FILE_TOOLS = {"Edit", "Write", "StrReplace", "Read"}
SHELL_TOOLS = {"Bash", "Shell"}


def format_tool_use(name: str, inp: dict) -> str:
    if name in SHELL_TOOLS:
        return f"\n> [{name}] {inp.get('command', '')}"
    if name in FILE_TOOLS:
        path = inp.get("file_path") or inp.get("path", "")
        return f"\n> [{name}] {path}"
    return f"\n> [{name}]"


def handle_assistant(event: dict) -> None:
    for block in event.get("message", {}).get("content", []):
        bt = block.get("type")
        if bt == "text":
            print(block["text"], flush=True)
        elif bt == "tool_use":
            print(format_tool_use(block.get("name", ""), block.get("input", {})), flush=True)


def handle_user(event: dict) -> None:
    """Print tool execution output (where env vars are resolved)."""
    result = event.get("tool_use_result")
    if not result:
        return
    if isinstance(result, str):
        if result.strip():
            print(result, flush=True)
        return
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    output = stdout or stderr
    if output and output.strip():
        print(output, flush=True)


def handle_result(event: dict) -> None:
    result = event.get("result", {})
    if isinstance(result, str):
        print(f"\n--- Result ---\n{result}", flush=True)
    else:
        for block in result.get("content", []):
            if block.get("type") == "text":
                print(f"\n--- Result ---\n{block['text']}", flush=True)

    cost = event.get("cost_usd")
    dur = event.get("duration_ms")
    if cost is not None:
        print(f"Cost: ${cost:.4f}", flush=True)
    if dur is not None:
        print(f"Duration: {dur / 1000:.1f}s", flush=True)


HANDLERS = {
    "assistant": handle_assistant,
    "user": handle_user,
    "result": handle_result,
}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    handler = HANDLERS.get(event.get("type", ""))
    if handler:
        handler(event)
