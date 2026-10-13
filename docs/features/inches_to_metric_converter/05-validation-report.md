# Validation report

Round 2 (re-validation after the code stage was reopened to close the rounding and whitespace test gaps). Validated against `docs/features/inches_to_metric_converter/02-requirements.md`, including its approved Assumptions.

## Test run
Run from the repo root (`/Users/dpallen77/sdlc-workflow`) on 2026-10-13. The command comes from `workflow.json` (`test_command`).

- `python3 -m pytest -q` gave `67 passed in 0.37s`
- `python3 -m pytest -q -rs` gave `67 passed in 0.36s`, with no skips listed
- `python3 -m pytest -q -v tests/inches_to_metric_converter/test_inches_to_metric_gui.py` gave `9 passed in 0.37s`, so the Tk GUI tests really ran and the `window` fixture did not skip

There were no failures and no skips. The suite has no tests for other features (`math_calculator` is still at `business_statement`), so there are no regressions.

Test counts: 56 in `test_inches_to_metric_core.py` (40 from round 1 plus 16 new parametrized cases), 9 in `test_inches_to_metric_gui.py`, 2 in `test_inches_to_metric_no_network.py`.

`src/` change check: `src/` is untracked in git, so I could not diff it. File times show all `src/inches_to_metric_converter/*.py` last modified at 11:35, and only `tests/inches_to_metric_converter/test_inches_to_metric_core.py` modified later (12:18). That matches the claim that only tests changed.

### New tests read in this round (all in `test_inches_to_metric_core.py`)
- `test_req_006_rounds_half_up`: 4 exact half-cent ties, "1.005" m to m gives "1.01", "2.345" m to m gives "2.35", "1.25" mm to cm (0.125) gives "0.13", "0.005" m to m gives "0.01". I checked each expected value by hand. Under round-half-even each would be different (1.00, 2.34, 0.12, 0.00), so these really tell the two rounding modes apart. The "0.005" case also agrees with the Assumption that only results *smaller than* 0.005 show "0.00".
- `test_req_004_ignores_surrounding_spaces`: " 2.5 ", "   2.5", "2.5   ", "\t2.5\t", " \t2.5 \n" feet to inches each give "30.00".
- `test_req_009_invalid_with_surrounding_spaces_shows_message`: " abc ", "  12ft  ", "   ", "\t" give "Please enter a valid number."
- `test_req_007_zero_or_negative_with_surrounding_spaces_shows_message`: " 0 ", "\t0.0\t", " -5 " give "Please enter a number greater than zero."

All of them assert exact string equality on `convert_text` output, so they can fail.

### Mutation checks (made on scratch copies outside the repo; the real code and tests were not changed)
| Mutation | Result |
|---|---|
| `quantize(..., rounding=ROUND_HALF_UP)` changed to `ROUND_HALF_EVEN` | Caught: `4 failed, 63 passed`, all 4 cases of `test_req_006_rounds_half_up` fail |
| `parse_amount`: `s = text.strip()` changed to `s = text` | Caught: `8 failed, 59 passed`, all 5 cases of `test_req_004_ignores_surrounding_spaces` and all 3 of `test_req_007_zero_or_negative_with_surrounding_spaces_shows_message` fail |
| `convert_text` calls `__import__("urllib.request").request.urlopen(...)` inside `try/except Exception: pass` | Not caught: `67 passed` (the known, accepted REQ-010 weakness; see Defects and gaps, item 1) |

Note: the whitespace-only invalid cases ("   ", "\t") still pass without stripping because the number regex rejects them either way. That is fine; the other 8 cases catch the mutation.

Both round-1 gaps (round half up, surrounding whitespace ignored) are now really closed.

### Edge-input probe (run through `convert_text`, meters to meters)
"+5" gives 5.00, ".5" gives 0.50, "5." gives 5.00, "1e3" / "1,000" / Arabic-Indic digit give "Please enter a valid number.", "0.004" gives 0.00, "0.005" gives 0.01.

## Requirement results
| Requirement | Criteria checked | Result (PASS/FAIL/GAP) | Evidence (test names, output) |
|---|---|---|---|
| REQ-001 | AC-1, AC-2 | PASS | `test_req_001_window_has_required_widgets` counts exactly 1 TEntry, 2 TCombobox, 1 TButton with text "Convert", and 1 widget named "result". `test_req_001_result_area_empty_on_open` asserts the result text is "". Both ran under real Tk (not skipped). |
| REQ-002 | AC-1 | PASS | `test_req_002_from_combo_values` reads the live "from" combobox values and asserts the exact ordered tuple and that "millimeters" is preselected. `test_req_002_from_units_list_order` checks `core.UNITS`. |
| REQ-003 | AC-1 | PASS | `test_req_003_to_combo_values` reads the live "to" combobox and asserts the exact ordered tuple and preselection. `test_req_003_to_units_list_order` checks `core.UNITS` and its length. |
| REQ-004 | AC-1 to AC-14 | PASS | `test_req_004_specific_conversions` has 13 cases, one per AC-1 to AC-13, with exact strings, checking both `convert` and `convert_text`. `test_req_004_all_56_pairs_match_assumed_factors` builds expected values from its own copy of the Assumptions' factors, asserts there are 56 pairs, and uses ROUND_HALF_UP (AC-14). Whitespace Assumption now covered by `test_req_004_ignores_surrounding_spaces` (mutation-verified). |
| REQ-005 | AC-1, AC-2, AC-3 | PASS | `test_req_005_meters_to_meters` ("7.00"), `test_req_005_inches_to_inches_rounds` ("3.14"), `test_req_005_each_unit_to_itself_is_one` (8 cases, each "1.00"). |
| REQ-006 | AC-1 to AC-4 | PASS | `test_req_006_convert_button_shows_two_decimals` fills the entry and both comboboxes, invokes the Convert button, and asserts the label is "39.37", "5.00", "30.48", "0.00". `test_req_006_display_two_decimals` checks the same in the core. Round-half-up Assumption now covered by `test_req_006_rounds_half_up` (mutation-verified). |
| REQ-007 | AC-1, AC-2, AC-3 | PASS | `test_req_007_zero_shows_message` (GUI, "0" and "0.0" with different unit pairs) and `test_req_007_zero_text_shows_message` (core) assert the output equals exactly the message, so no number is shown. `test_req_007_convert_zero_raises` asserts `NonPositiveValueError`, so no value is returned. `test_req_007_zero_or_negative_with_surrounding_spaces_shows_message` adds padded cases. |
| REQ-008 | AC-1, AC-2, AC-3 | PASS | `test_req_008_negative_shows_message` (GUI, "-5" and "-0.01"), `test_req_008_negative_text_shows_message` (core), `test_req_008_convert_negative_raises` (`convert(-1, ...)` raises `NonPositiveValueError`). |
| REQ-009 | AC-1 to AC-4 | PASS | `test_req_009_invalid_shows_message` (GUI: "", "abc", "12ft" each show exactly "Please enter a valid number."), `test_req_009_invalid_text_shows_message` (core), `test_req_009_convert_invalid_raises`, `test_req_009_valid_after_error_replaces_message` (error, then "1" inches to millimeters shows exactly "25.40", so the error is gone), plus `test_req_009_invalid_with_surrounding_spaces_shows_message`. |
| REQ-010 | AC-1, AC-2 | PASS (weak test, known and accepted; see item 1) | `test_req_010_converts_with_network_blocked` stubs `socket.socket` and `socket.create_connection` to raise, then asserts "25.40". `test_req_010_source_imports_no_network_modules` AST-checks every `.py` in the package against a list of network modules. I read the code: `core.py` imports only `re` and `decimal`; `gui.py` imports only `tkinter`/`ttk` and `.core`. Neither makes a network call. |

## Defects and gaps
No new defects. The two round-1 gaps are closed:

- Closed (round-1 item 2): round half up is now tested by `test_req_006_rounds_half_up`; switching to ROUND_HALF_EVEN fails 4 tests.
- Closed (round-1 item 3): surrounding whitespace is now tested by `test_req_004_ignores_surrounding_spaces` and related padded-input tests; removing `strip()` fails 8 tests.

Known, accepted, non-blocking items (the human chose not to address these; stated here for the record):

1. REQ-010, weak network test (accepted). `test_req_010_converts_with_network_blocked` only checks the final result, not that no network call was attempted, and the AST check only sees static `import` statements. A mutation that calls `__import__("urllib.request").request.urlopen(...)` inside `try/except Exception: pass` still passes all 67 tests. The current code makes no network calls (verified by reading it), so REQ-010 is met today. The test would not catch that kind of future regression.
2. Lenient number forms (accepted). The core accepts "+5" (5.00), ".5" (0.50), and "5." (5.00). These are valid numbers, and no requirement says they must be rejected, so this does not violate REQ-009. Scientific notation ("1e3"), thousands separators ("1,000"), and non-ASCII digits are rejected with "Please enter a valid number."

Other observations (informational): the core raises `UnknownUnitError` for unknown unit names. The GUI can't reach this because both comboboxes are read-only. No secrets found in `src/inches_to_metric_converter/` or `tests/inches_to_metric_converter/`.

## Verdict
PASS. Every acceptance criterion of REQ-001 to REQ-010 has a test that really asserts it, the full suite passed 67/67 with no skips, and mutation testing confirms the two round-1 gaps (round half up, whitespace ignored) are now really covered.
