# Design

## Overview
The feature is a small Python package, `inches_to_metric_converter`, under `src/`. It has two layers. A pure core module (`core.py`) holds the 8 units and their exact meters-per-unit factors. It parses the entry text, checks that the value is valid and positive, and converts using `decimal.Decimal` arithmetic, rounding half up to 2 decimal places. It also produces the exact string the result area should show, which is either the number or one of the two fixed error messages. A thin tkinter module (`gui.py`) builds the window: one entry, two read-only drop-downs, a "Convert" button, and a result label. When the button is pressed, it passes the entry text and the two selected units to the core and puts the returned string in the result label. The GUI does no arithmetic and no validation of its own. Because of this split, every conversion, rounding, and error-message rule can be tested headlessly. Only the widget layout and the button wiring need a Tk interpreter.

## Components
All components are new. `src/` was empty, and no other feature's design exists yet, so no existing component is changed.

1. **Package `src/inches_to_metric_converter/__init__.py`** (new)
   - Responsibility: marks the package. It re-exports the public core names (`UNITS`, `convert`, `convert_text`, the error classes, and the message constants).
   - Must not: import `gui` or `tkinter`. Importing the package must work on a machine with no display and no Tk.

2. **Core module `src/inches_to_metric_converter/core.py`** (new)
   - Responsibility: the unit list and order, the conversion factors, parsing the entry text, the zero/negative/invalid checks, converting, rounding half up to 2 decimal places, and formatting the result as a string with exactly 2 decimal places.
   - Must not: import `tkinter` or any networking module, read files, read the environment, or keep state between calls.

3. **GUI module `src/inches_to_metric_converter/gui.py`** (new)
   - Responsibility: build the window inside a given Tk root, preselect the first unit in both drop-downs, start with an empty result area, and on "Convert" show `core.convert_text(...)` in the result label.
   - Must not: do arithmetic, parse numbers, choose error messages, or keep its own copy of the unit list. It reads `core.UNITS`. It must not create a `Tk()` root inside `ConverterWindow`; only `main()` creates one.

4. **Entry point `src/inches_to_metric_converter/__main__.py`** (new)
   - Responsibility: `from .gui import main; main()`, so the app starts with `PYTHONPATH=src python3 -m inches_to_metric_converter` from the repo root.
   - Must not: contain any logic.

5. **Test support `tests/inches_to_metric_converter/conftest.py`** (new; written by the engineer at the code stage)
   - Responsibility: put `<repo>/src` at the front of `sys.path` if it is not already there, and provide the `window` fixture for GUI tests (see Interfaces).
   - Must not: change any other feature's tests or require a repo-wide `pytest.ini` or `pyproject.toml`.

## Interfaces and data

### Module paths and imports
| File | Import as |
|---|---|
| `src/inches_to_metric_converter/__init__.py` | `import inches_to_metric_converter` |
| `src/inches_to_metric_converter/core.py` | `from inches_to_metric_converter import core` or `from inches_to_metric_converter.core import convert, convert_text, UNITS` |
| `src/inches_to_metric_converter/gui.py` | `from inches_to_metric_converter.gui import ConverterWindow` |
| `src/inches_to_metric_converter/__main__.py` | run with `PYTHONPATH=src python3 -m inches_to_metric_converter` |

Tests live in `tests/inches_to_metric_converter/` and run with `python3 -m pytest -q` from the repo root. `tests/inches_to_metric_converter/conftest.py` does:
```python
import sys, pathlib
SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
```
Both `tests/__init__.py` and `tests/inches_to_metric_converter/__init__.py` exist and are empty. Because both are present, pytest names the test package `tests.inches_to_metric_converter`, so it does not shadow the real `inches_to_metric_converter` package in `src/`, and same-named test files in different features do not collide. Tests import the code with `from inches_to_metric_converter.core import ...`. Test files still use distinctive feature-prefixed names:
- `tests/inches_to_metric_converter/test_inches_to_metric_core.py` for headless tests of core
- `tests/inches_to_metric_converter/test_inches_to_metric_gui.py` for tests that need Tk
- `tests/inches_to_metric_converter/test_inches_to_metric_no_network.py` for the source inspection and no-network tests

### Data (in `core.py`)
```python
UNITS: tuple[str, ...] = ("millimeters", "centimeters", "meters", "kilometers",
                          "inches", "feet", "yards", "miles")

METERS_PER_UNIT: dict[str, Decimal] = {
    "millimeters": Decimal("0.001"),
    "centimeters": Decimal("0.01"),
    "meters":      Decimal("1"),
    "kilometers":  Decimal("1000"),
    "inches":      Decimal("0.0254"),
    "feet":        Decimal("0.3048"),
    "yards":       Decimal("0.9144"),
    "miles":       Decimal("1609.344"),
}

MSG_NOT_POSITIVE = "Please enter a number greater than zero."
MSG_INVALID      = "Please enter a valid number."
```

### Errors (in `core.py`)
```python
class ConversionError(ValueError):            # base; .message holds the display text
    message: str
class InvalidNumberError(ConversionError):    # message == MSG_INVALID
class NonPositiveValueError(ConversionError): # message == MSG_NOT_POSITIVE
class UnknownUnitError(ConversionError):      # message names the bad unit; not reachable from the GUI
```

### Functions (in `core.py`)
```python
def parse_amount(text: str) -> Decimal
```
- Strips surrounding whitespace with `str.strip()`.
- Accepts only plain decimal notation: `re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", s, re.ASCII)`.
- Raises `InvalidNumberError` if the text is empty or does not match. Examples: `""`, `"abc"`, `"12ft"`, `"1e3"`, `"nan"`, `"inf"`, `"1,000"`, `"1_000"`.
- Returns `Decimal(s)`. It does **not** check the sign; `convert` does that.

```python
def convert(value: Decimal | int | float | str, from_unit: str, to_unit: str) -> Decimal
```
- Turns `value` into a `Decimal` with `Decimal(str(value))`. A non-finite or unparseable value raises `InvalidNumberError`.
- If `value <= 0` (this includes `-0`), raises `NonPositiveValueError`. No value is returned.
- If either unit is not in `METERS_PER_UNIT`, raises `UnknownUnitError`.
- Computes `value * METERS_PER_UNIT[from_unit] / METERS_PER_UNIT[to_unit]` inside `decimal.localcontext()`, with `prec = max(value.adjusted(), 0) + 40`. That is enough digits for the quotient to be exact well past the cents digit for any input size.
- Returns `result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`. So `str()` of the return value always has exactly 2 decimal places, for example `Decimal("25.40")`, `Decimal("1000.00")`, or `Decimal("0.00")`.
- When `from_unit == to_unit`, the same formula gives the value rounded to 2 decimal places. No special case is needed.

```python
def format_result(value: Decimal) -> str
```
- Returns `format(value, "f")` of the already-quantized value. This gives plain digits, no exponent, no separators, and no unit.

```python
def convert_text(text: str, from_unit: str, to_unit: str) -> str
```
- Runs `parse_amount`, then `convert`, then `format_result`. If a `ConversionError` is raised, it returns `err.message`.
- This is the only function the GUI calls. It returns exactly the string that the result area must show.

### GUI (in `gui.py`)
```python
class ConverterWindow:
    def __init__(self, root: tkinter.Misc) -> None
    entry: ttk.Entry           # Tk widget name "amount"
    from_combo: ttk.Combobox   # name "from_unit", values=core.UNITS, state="readonly", current(0)
    to_combo: ttk.Combobox     # name "to_unit",   values=core.UNITS, state="readonly", current(0)
    convert_button: ttk.Button # name "convert", text="Convert", command=self.on_convert
    result_label: ttk.Label    # name "result", text="" initially
    def on_convert(self) -> None   # result_label.configure(text=core.convert_text(entry.get(), from_combo.get(), to_combo.get()))
    def result_text(self) -> str   # str(result_label.cget("text"))

def main() -> None   # root = tkinter.Tk(); root.title("Distance Converter"); ConverterWindow(root); root.mainloop()
```
- The layout uses `grid`. Two caption `ttk.Label`s, "From:" and "To:", may sit next to the drop-downs. Only the widget named `result` is the result area.
- The result label's text is set directly with `configure(text=...)` and not through a `StringVar`. That way, `cget("text")` returns exactly what is on screen.
- Each conversion overwrites the result label. A later valid conversion therefore fully replaces an earlier error message, and an error fully replaces an earlier number.

### GUI test fixture (in `conftest.py`)
```python
@pytest.fixture
def window():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tk not available (no display): {e}")
    root.withdraw()
    w = ConverterWindow(root)
    root.update_idletasks()
    yield w
    root.destroy()
```
GUI tests drive the window like this: `w.entry.delete(0, "end")`, then `w.entry.insert(0, "1")`, then `w.from_combo.set("meters")`, `w.to_combo.set("inches")`, then `w.convert_button.invoke()`, and finally they assert on `w.result_text()`. `invoke()` runs the button's command synchronously, so the tests need no event loop and no window ever has to be visible.

## Key decisions
1. **Use `Decimal` arithmetic instead of `float`.** Alternatives: `float` with `round()`, or `float` with `"%.2f"`. Python's `round()` is round-half-even, and binary floats misrepresent values like 0.0254. Both can produce off-by-one-cent results at ties and near ties, so neither meets the "round half up" assumption reliably. `Decimal` with exact string factors and `ROUND_HALF_UP` gives exactly the rule REQ-004 AC-14 describes. It is in the standard library.
2. **Use a single meters-per-unit table instead of a pairwise table.** A pairwise table would need 56 entries and could drift out of sync. The single table has 8 entries, and every pair is derived from it, as REQ-004 AC-14 specifies.
3. **Put display strings in the core (`convert_text`), not in the GUI.** The alternative was letting the GUI catch exceptions and choose the messages. Keeping it in the core means every REQ-006 to REQ-009 display rule can be tested headlessly. The GUI tests then only confirm the wiring.
4. **Signal errors from `convert` by raising, not by returning `None` or a sentinel.** REQ-007 AC-3 and REQ-008 AC-3 require that it "signals an error and returns no converted value". A raised exception means there is no return value at all, and tests can check it with `pytest.raises(NonPositiveValueError)`.
5. **Accept only plain decimal notation, using a strict regex.** The alternatives were `float(text)` or `Decimal(text)`, which also accept `"1e3"`, `"nan"`, `"inf"`, `"1_000"`, and non-ASCII digits. The requirements only call decimal input such as "2.5" valid, and they rule out scientific notation in the output. The strict pattern keeps "valid number" predictable, rejects `"12ft"`, and still accepts a leading sign. The sign has to be accepted so that `"-5"` gets the "greater than zero" message rather than "valid number".
6. **Use read-only comboboxes with the first unit preselected.** This matches the assumption that there is never a "no unit selected" state. The user cannot type a unit that does not exist, so `UnknownUnitError` only guards direct API calls.
7. **Use a self-contained package plus a per-feature `conftest.py`, with no repo-wide pytest config.** The alternative was adding `pythonpath = src` to a root `pytest.ini`. That would be a shared file other features would have to edit. The per-feature conftest is idempotent, and prefixed test file names avoid basename clashes with future features.
8. **Use widget names and attributes for test lookup.** The REQ-001 test counts widgets by Tk class across the whole widget tree. `ttk.Combobox` is a Python subclass of `ttk.Entry`, so `isinstance` would count the drop-downs as entries. The test therefore uses `winfo_class()` (`TEntry`, `TCombobox`, `TButton`) and the fixed widget name `result`.
9. **Add nothing extra.** There is no Enter-key binding, no unit label in the result, no history, and no command-line interface. None of these is required, and the CLI is explicitly out of scope.

## Error handling and limits
- **Empty or non-numeric entry:** `InvalidNumberError`, shown as "Please enter a valid number." No number is shown.
- **Zero, negative, or `-0`:** `NonPositiveValueError`, shown as "Please enter a number greater than zero." No number is shown.
- **Unknown unit (API misuse only):** `UnknownUnitError`. `convert_text` returns its message. It cannot happen through the GUI.
- **Very large input:** the `Decimal` precision grows with the size of the input (`adjusted() + 40`), so a valid number never overflows or loses the cents digit. There is no artificial input length limit.
- **Very small results:** values below 0.005 round to `0.00`, as the assumptions require. Values of exactly 0.005 or more round up to `0.01`.
- **Retries:** none. Every operation is local and deterministic.
- **Security and network:** neither `core.py` nor `gui.py` imports `socket`, `ssl`, `urllib`, `http`, `requests`, `urllib3`, `httpx`, `ftplib`, `smtplib`, `xmlrpc`, `socketserver`, or `asyncio`, and nothing reads `.env` or any secrets. There are no secrets in this feature.
- **Tk unavailable:** importing `core` never touches tkinter. `main()` lets `TclError` propagate with Tk's own message, for example "no display name". The test fixture turns this into an explicit skip.

### What needs a display
- **Headless (no Tk at all):** all of REQ-004, REQ-005, and REQ-010. Also every display-string rule in REQ-006 to REQ-009, tested through `convert_text`, and the drop-down contents through `core.UNITS`.
- **Needs a Tk interpreter (but no visible window, because the root is withdrawn):** REQ-001 AC-1 and AC-2; REQ-002 AC-1 and REQ-003 AC-1 as read from the actual comboboxes; and the "when Convert is pressed" form of REQ-006 to REQ-009, using `convert_button.invoke()`.
- On macOS, Tk works in a normal logged-in session, so these tests run on this development machine. It may fail over SSH or in a headless CI runner. On Linux CI, run under `xvfb-run python3 -m pytest -q`.
- If Tk cannot start, the GUI tests are **skipped** and pytest still exits 0. The validator must therefore read the pytest summary and treat any skipped GUI test as "not verified", not as passed.

## Traceability
| Requirement | Component(s) | How it is satisfied |
|---|---|---|
| REQ-001 | `gui.ConverterWindow`, `gui.main`, `__main__` | The window contains exactly one `TEntry` (`amount`), two `TCombobox` (`from_unit`, `to_unit`), one `TButton` "Convert", and one result label (`result`) whose initial text is `""`. Tested in the Tk fixture by walking the widget tree with `winfo_class()` and by checking `result_text() == ""`. |
| REQ-002 | `core.UNITS`, `gui.ConverterWindow.from_combo` | `from_combo` values come from `core.UNITS` in the required order. Tested headlessly on `UNITS` and in Tk on `tuple(map(str, from_combo["values"]))`. |
| REQ-003 | `core.UNITS`, `gui.ConverterWindow.to_combo` | `to_combo` uses the same `core.UNITS` tuple. Tested the same way as REQ-002 on `to_combo`. |
| REQ-004 | `core.METERS_PER_UNIT`, `core.convert`, `core.parse_amount` | `Decimal` value × from factor ÷ to factor, quantized to 0.01 with `ROUND_HALF_UP`. AC-1 to AC-13 are asserted directly. For AC-14 the test builds its own factor table from the Assumptions (it does not import `METERS_PER_UNIT`) and checks all 56 pairs. |
| REQ-005 | `core.convert` | The same formula with identical factors returns the value rounded to 2 decimal places. Tested with 7 m to m, 3.14159 in to in, and all 8 units to themselves. |
| REQ-006 | `core.format_result`, `core.convert_text`, `gui.ConverterWindow.on_convert` | The quantized `Decimal` is formatted with `"f"`, giving exactly 2 decimal places and no unit or separators. Tested headlessly through `convert_text`, and in Tk through `convert_button.invoke()` and `result_text()` for "39.37", "5.00", "30.48", and "0.00". |
| REQ-007 | `core.convert` (`NonPositiveValueError`), `core.convert_text`, `gui.on_convert` | `value <= 0` raises, so nothing is returned. `convert_text` returns `MSG_NOT_POSITIVE`. Tested with `pytest.raises` for value 0, and in Tk for "0" and "0.0". |
| REQ-008 | `core.convert` (`NonPositiveValueError`), `core.convert_text`, `gui.on_convert` | Same path as REQ-007 for negative values. Tested with `pytest.raises` for -1, and in Tk for "-5" and "-0.01". |
| REQ-009 | `core.parse_amount` (`InvalidNumberError`), `core.convert_text`, `gui.on_convert` | The strict decimal regex rejects "", "abc", and "12ft", and `MSG_INVALID` is shown. The label is overwritten on every press, so a following valid "1" inches to millimeters shows "25.40" with no leftover error. Tested in Tk with a sequence of two presses. |
| REQ-010 | `core.py`, `gui.py` (no network imports) | The factors are constants in `core.py`. AC-1: the test monkeypatches `socket.socket` (and `socket.create_connection`) to raise, then converts 1 inches to millimeters and expects "25.40". AC-2: the test parses every `.py` file in `src/inches_to_metric_converter/` with `ast` and asserts that no `import`/`from` root name is in the networking list above. |
