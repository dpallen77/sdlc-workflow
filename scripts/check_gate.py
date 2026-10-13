"""Deterministic stage gates. The model cannot talk its way past these.

Usage: python3 scripts/check_gate.py <feature> <stage> [--skip-tests]
Stages: business_statement | requirements | design | code | validation
Exit code 0 = gate passed, 1 = gate failed (reasons are printed).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES = ROOT / "docs" / "features"
FEATURE_NAME = re.compile(r"[a-z][a-z0-9_]*")
REQ_ID = re.compile(r"REQ-\d{3}")
# Unfilled template slots like "[desktop window / CLI]" or "<add yours>". "[text](url)" links don't count.
PLACEHOLDER = re.compile(r"\[[^\]\n]+\](?!\()|<[^<>\n]+>")
SKIPPED = re.compile(r"\b(\d+) skipped\b")


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def rel(path):
    return path.relative_to(ROOT).as_posix()


def load_requirements(docs):
    """Returns ({id: block_text}, [problems])."""
    path = docs / "02-requirements.md"
    text = read(path)
    if text is None:
        return {}, [f"{rel(path)} does not exist"]
    reqs, problems = {}, []
    for block in re.split(r"(?m)^###\s+(?=REQ-\d{3})", text)[1:]:
        rid = block[:7]
        if rid in reqs:
            problems.append(f"{rid} is defined more than once")
        reqs[rid] = block
    if not reqs:
        problems.append("no requirements found (expected headings like '### REQ-001: Title')")
    if re.search(r"\b(TBD|TODO)\b|\?\?", text):
        problems.append("unresolved TBD/TODO/?? markers remain in the requirements")
    return reqs, problems


def run_tests(docs):
    """Runs the whole suite, not just this feature's tests, so regressions in other features fail the gate."""
    try:
        cmd = json.loads((ROOT / "workflow.json").read_text()).get("test_command")
    except (OSError, ValueError):
        cmd = None
    cmd = cmd or "python3 -m pytest -q"
    result = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    out = result.stdout + result.stderr
    (docs / "test-results.txt").write_text(
        f"$ {cmd}\n(exit code {result.returncode})\n\n{out}", encoding="utf-8")
    if result.returncode != 0:
        tail = "\n".join(out.strip().splitlines()[-15:])
        return [f"tests did not pass (exit code {result.returncode}):\n{tail}"]
    # pytest exits 0 when tests are skipped, but a skipped test verified nothing.
    skipped = SKIPPED.search(out)
    if skipped:
        return [f"{skipped.group(1)} test(s) were skipped; a skipped test is not a pass. "
                f"Run '{cmd} -rs' to see why, and fix the cause (e.g. no display for GUI tests)"]
    return []


def gate_business_statement(docs):
    path = docs / "01-business-statement.md"
    text = read(path)
    if text is None:
        return [f"{rel(path)} does not exist"]
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    words = len(re.findall(r"\w+", body))
    problems = [] if words >= 50 else [f"business statement looks unfinished ({words} words; need at least 50)"]
    problems += [f"unfilled placeholder: {p}" for p in PLACEHOLDER.findall(body)]
    if re.search(r"\b(TBD|TODO)\b|\?\?", body):
        problems.append("unresolved TBD/TODO/?? markers remain in the business statement")
    return problems


def gate_requirements(docs):
    reqs, problems = load_requirements(docs)
    for rid, block in reqs.items():
        if not re.search(r"(?m)^\s*-\s*AC-\d+", block):
            problems.append(f"{rid} has no acceptance criteria (need lines like '- AC-1: ...')")
    return problems


def gate_design(docs):
    reqs, problems = load_requirements(docs)
    path = docs / "03-design.md"
    design = read(path)
    if design is None:
        return problems + [f"{rel(path)} does not exist"]
    problems += [f"{r} is not addressed in the design" for r in reqs if r not in design]
    problems += [f"design mentions {r}, which is not a defined requirement"
                 for r in sorted(set(REQ_ID.findall(design)) - set(reqs))]
    return problems


def gate_code(feature, docs, skip_tests):
    reqs, problems = load_requirements(docs)
    tests_dir = ROOT / "tests" / feature
    files = sorted(tests_dir.rglob("*.py")) if tests_dir.exists() else []
    if not files:
        return problems + [f"no test files found in tests/{feature}/"]
    text = "\n".join(f.read_text(encoding="utf-8") for f in files).lower()
    for r in reqs:
        if r.lower() not in text and r.lower().replace("-", "_") not in text:
            problems.append(f"{r} has no test in tests/{feature}/ "
                            f"(use '{r.lower().replace('-', '_')}' in a test name or docstring)")
    if not skip_tests:
        problems += run_tests(docs)
    return problems


def gate_validation(docs, skip_tests):
    reqs, problems = load_requirements(docs)
    path = docs / "05-validation-report.md"
    report = read(path)
    if report is None:
        return problems + [f"{rel(path)} does not exist"]
    problems += [f"{r} is missing from the validation report" for r in reqs if r not in report]
    if not re.search(r"(?mi)^##\s+Verdict", report):
        problems.append("report has no '## Verdict' section")
    if not skip_tests:
        problems += run_tests(docs)
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    skip = "--skip-tests" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 2
    feature, stage = args
    docs = FEATURES / feature
    gates = {"business_statement": lambda: gate_business_statement(docs),
             "requirements": lambda: gate_requirements(docs),
             "design": lambda: gate_design(docs),
             "code": lambda: gate_code(feature, docs, skip),
             "validation": lambda: gate_validation(docs, skip)}
    if stage not in gates:
        print(__doc__)
        return 2
    if not FEATURE_NAME.fullmatch(feature) or not docs.is_dir():
        print(f"Unknown feature '{feature}' (no folder {rel(docs)}/).")
        return 2
    problems = gates[stage]()
    if problems:
        print(f"GATE FAILED: {feature} {stage}")
        for p in problems:
            print(f" - {p}")
        return 1
    print(f"GATE PASSED: {feature} {stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
