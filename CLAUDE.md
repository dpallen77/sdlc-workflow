# SDLC workflow project

This repo builds one product, one feature at a time or several in parallel. Each feature goes through five stages. Each stage produces a file, and a human approves it before that feature's next stage starts.

Every feature has a short name (lowercase, digits and underscores, e.g. `user_login`). Below, `<feature>` means that name.

| Stage | Who | Artifact |
|---|---|---|
| `business_statement` | the human writes it | `docs/features/<feature>/01-business-statement.md` |
| `requirements` | `requirements-analyst` | `docs/features/<feature>/02-requirements.md` |
| `design` | `designer` | `docs/features/<feature>/03-design.md` |
| `code` | `engineer` | `src/` and `tests/<feature>/` |
| `validation` | `validator` | `docs/features/<feature>/05-validation-report.md` |

## Rules (read these first, every session)
1. Read `workflow.json` at the start. Each entry under `features` has its own `stage`. Work on the feature the human names; if they don't name one and more than one feature is active, ask which. Work only on that feature's current stage. Never start a later stage.
2. Never edit `workflow.json`, `CLAUDE.md`, `scripts/`, or `.claude/`. Never run `scripts/approve.py`. Only the human starts features and approves stages. A hook blocks these edits; do not try to work around it.
3. Use the matching subagent for each stage, and tell it the feature name. Do not do a stage's work yourself in the main conversation.
4. Subagents cannot ask the user questions. If a subagent returns open questions, ask the human, then re-delegate with the answers.
5. When a stage's artifact is written, run `python3 scripts/check_gate.py <feature> <stage>`, report the result, and STOP. Ask the human to review and run `python3 scripts/approve.py <feature> <stage>`.
6. Never say tests pass unless you ran them in this session. Quote the real result.
7. If validation finds defects, report them and stop. The human reopens the code stage with `python3 scripts/approve.py <feature> reopen code`. After 3 failed fix cycles, stop and escalate instead of trying again.

## Conventions
- Requirements are numbered `REQ-001`, `REQ-002`, ... within each feature (every feature starts at REQ-001). Each has acceptance criteria numbered `AC-1`, `AC-2`, ...
- A design must mention every `REQ-` ID of its feature and no ID that doesn't exist there.
- A feature's tests live in `tests/<feature>/`. Test functions are named `test_req_001_<what_it_checks>`, and each requirement has at least one.
- Tests are written from the acceptance criteria, before or alongside the code, never fitted to the code afterward.
- The gates run the whole test suite, so a feature can't pass while it breaks another feature's tests.
- `src/` is shared. Prefer having only one feature in the code stage at a time.

## Project constraints (fill these in)
- Language and stack: Python 3, standard library where possible
- Test runner: pytest (command is set in `workflow.json`)
- Secrets: never commit keys; read them from `.env`
- Budget / other limits: <add yours>

