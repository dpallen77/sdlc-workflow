#!/usr/bin/env python3
"""Human-only approval. Run this yourself in a terminal, not through Claude.

Usage:
  python3 scripts/approve.py new <feature>               start a feature and create its business statement
  python3 scripts/approve.py <feature> <stage>           run the gate; if it passes, approve and advance
  python3 scripts/approve.py <feature> reopen <stage>    reopen a stage (and everything after it)
  python3 scripts/approve.py status                      show every feature's current stage
Feature names: lowercase letters, digits and underscores, starting with a letter (e.g. user_login).
Stages: business_statement | requirements | design | code | validation
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "workflow.json"
FEATURES = ROOT / "docs" / "features"
STAGES = ["business_statement", "requirements", "design", "code", "validation"]
FEATURE_NAME = re.compile(r"[a-z][a-z0-9_]*")
RESERVED = {"new", "status", "reopen"}

TEMPLATE = """# Business statement

<!-- Write this yourself, in plain language. Aim for 100-300 words. The gate needs at least 50 words outside comments. -->

## Problem
<!-- What is going wrong or missing today, and for whom? -->

## Users
<!-- Who will use this? -->

## Desired outcome
<!-- What should be true when this works? -->

## Constraints
<!-- Budget, tools, deadlines, rules that must hold -->

## Out of scope
<!-- What this should NOT do -->

## Success measures
<!-- How you will know it worked -->
"""


def load():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state.setdefault("features", {})
    return state


def save(state):
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def new_feature(state, name):
    if not FEATURE_NAME.fullmatch(name) or name in RESERVED:
        print(f"Bad feature name '{name}'. Use lowercase letters, digits and underscores, starting with a letter.")
        return 1
    if name in state["features"]:
        print(f"Feature '{name}' already exists (stage: {state['features'][name]['stage']}).")
        return 1
    docs = FEATURES / name
    docs.mkdir(parents=True, exist_ok=True)
    statement = docs / "01-business-statement.md"
    if not statement.exists():
        statement.write_text(TEMPLATE, encoding="utf-8")
    state["features"][name] = {"stage": STAGES[0], "approved": {s: False for s in STAGES}}
    save(state)
    print(f"Started feature '{name}'.")
    print(f"Write {statement.relative_to(ROOT).as_posix()}, then run: "
          f"python3 scripts/approve.py {name} business_statement")
    return 0


def main():
    args = sys.argv[1:]
    state = load()
    features = state["features"]

    if args == ["status"]:
        if not features:
            print("No features yet. Start one with: python3 scripts/approve.py new <feature>")
        for name in sorted(features):
            print(f"{name:<30} {features[name]['stage']}")
        return 0

    if len(args) == 2 and args[0] == "new":
        return new_feature(state, args[1])

    if args and args[0] not in RESERVED and args[0] not in features:
        print(f"Unknown feature '{args[0]}'. Known: {', '.join(sorted(features)) or 'none'}")
        return 1

    if len(args) == 3 and args[1] == "reopen" and args[2] in STAGES:
        name, stage = args[0], args[2]
        feature = features[name]
        for s in STAGES[STAGES.index(stage):]:
            feature["approved"][s] = False
        feature["stage"] = stage
        save(state)
        print(f"Reopened '{name}' at '{stage}'.")
        return 0

    if len(args) == 2 and args[1] in STAGES:
        name, stage = args
        feature = features[name]
        if feature["stage"] != stage:
            print(f"Feature '{name}' is at stage '{feature['stage']}', not '{stage}'.")
            return 1
        rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_gate.py"), name, stage]).returncode
        if rc != 0:
            print("Not approved: fix the gate failures above first.")
            return 1
        feature["approved"][stage] = True
        i = STAGES.index(stage)
        feature["stage"] = STAGES[i + 1] if i + 1 < len(STAGES) else "done"
        save(state)
        print(f"Approved '{name}' {stage}. Now at: {feature['stage']}")
        coding = [f for f in features if f != name and features[f]["stage"] == "code"]
        if feature["stage"] == "code" and coding:
            print(f"Note: {', '.join(coding)} is also in the code stage. Both share src/, "
                  "so consider finishing one before building the other.")
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())