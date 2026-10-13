#!/usr/bin/env python3
"""PreToolUse hook. Claude Code sends the pending tool call as JSON on stdin.
Exit 0 = allow. Exit 2 = block, and the stderr message goes back to Claude.

It fails closed: if workflow.json can't be read, edits are blocked.
Limit: this is a guardrail, not a security boundary. A determined shell command
could still write files, so keep the approval step (approve.py) human-only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALWAYS_BLOCKED = {"workflow.json", "CLAUDE.md"}
ALWAYS_BLOCKED_PREFIXES = ("scripts/", ".claude/")
FEATURE_DOC_RULES = {  # file inside docs/features/<feature>/ -> that feature's stages in which Claude may write it
    "02-requirements.md": {"requirements"},
    "03-design.md": {"design"},
    "05-validation-report.md": {"validation"},
}


def block(msg):
    print(f"BLOCKED: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    try:
        call = json.load(sys.stdin)
    except ValueError:
        block("could not read the hook input")
    tool = call.get("tool_name", "")
    tool_input = call.get("tool_input") or {}

    try:
        features = json.loads((ROOT / "workflow.json").read_text(encoding="utf-8")).get("features")
        stages = {name: f["stage"] for name, f in features.items()}
    except (OSError, ValueError, AttributeError, KeyError, TypeError):
        block("workflow.json is missing, unreadable, or not in the multi-feature format")

    if tool == "Bash":
        cmd = tool_input.get("command", "")
        for word in ("workflow.json", "approve.py", ".claude/"):
            if word in cmd:
                block(f"commands touching '{word}' are not allowed. Only the human approves stages.")
        return

    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return
    p = Path(path)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    try:
        rel = p.relative_to(ROOT).as_posix()
    except ValueError:
        return  # outside this project

    if rel in ALWAYS_BLOCKED or rel.startswith(ALWAYS_BLOCKED_PREFIXES):
        block(f"'{rel}' is a protected control file. Only the human edits it.")

    parts = rel.split("/")
    if parts[:2] == ["docs", "features"] and len(parts) >= 3:
        feature = parts[2]
        if feature not in stages:
            block(f"'{rel}' belongs to unknown feature '{feature}'. The human starts features with approve.py new.")
        allowed = FEATURE_DOC_RULES.get("/".join(parts[3:]))
        if allowed is None:
            block(f"'{rel}' is human- or gate-owned. Claude writes only {', '.join(FEATURE_DOC_RULES)} here.")
        if stages[feature] in allowed:
            return
        block(f"'{rel}' cannot be changed while '{feature}' is in stage '{stages[feature]}' "
              f"(allowed in: {', '.join(sorted(allowed))}).")

    if parts[0] == "tests" and len(parts) >= 3 and parts[1] in stages:
        feature = parts[1]
        if stages[feature] == "code":
            return
        block(f"'{rel}' cannot be changed while '{feature}' is in stage '{stages[feature]}' (allowed in: code).")

    # src/, shared test files (tests/__init__.py, tests/conftest.py) and anything else: any feature in code.
    if "code" not in stages.values():
        block(f"'{rel}' can only be changed while a feature is in the code stage (none is).")


if __name__ == "__main__":
    main()
