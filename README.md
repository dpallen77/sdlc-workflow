# SDLC workflow starter

Five stages per feature, each with a file, a gate check, and a human approval:
business statement -> requirements -> design -> code/tests -> validation.
Several features can be in flight at once; each has its own folder and its own stage.

## Setup
1. Copy this whole folder into a new project folder and run `git init`.
2. Open the folder in VS Code and start Claude Code. Run `/init` only if you want it to regenerate CLAUDE.md (this one is already written, so you can skip it).
3. `python3 -m pip install pytest` (or change `test_command` in workflow.json).
4. On Windows, change `python3` to `python` in `.claude/settings.json`.

## Running a feature
1. Start it: `python3 scripts/approve.py new user_login`. This creates `docs/features/user_login/01-business-statement.md`.
2. Write that business statement yourself, then run `python3 scripts/approve.py user_login business_statement`.
3. In Claude Code: "Run the requirements stage for user_login." It uses the requirements-analyst subagent, runs the gate, and stops.
4. Review the file. If it's good, run `python3 scripts/approve.py user_login requirements` in your own terminal.
5. Repeat for design, code, and validation.
6. If validation finds defects: `python3 scripts/approve.py user_login reopen code`.
7. See where every feature stands: `python3 scripts/approve.py status`.

## Layout
```
docs/features/<feature>/   01-business-statement.md, 02-requirements.md, 03-design.md,
                           05-validation-report.md, test-results.txt
src/                       shared code
tests/<feature>/           that feature's tests
```

## Working on features in parallel
- Requirements and design for different features can run side by side.
- `src/` is shared, so keep only one feature in the code stage at a time where you can. `approve.py` warns you when a second one enters it.
- Every gate runs the whole test suite. A feature that breaks another feature's tests fails its gate.

## Files you edit by hand
Each feature's `01-business-statement.md`, `workflow.json` (only `test_command`), and `CLAUDE.md` (project constraints). Claude is blocked from editing everything under `scripts/` and `.claude/`.

## Notes
- The hook is a guardrail, not a security boundary. Keep `approve.py` human-only.
- Restart Claude Code after the first time `.claude/agents/` is created, so it picks up the agents.
