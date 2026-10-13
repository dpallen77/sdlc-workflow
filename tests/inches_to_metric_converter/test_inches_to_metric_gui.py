"""Tk tests: widget layout and the "Convert" button wiring."""

EXPECTED_UNITS = (
    "millimeters", "centimeters", "meters", "kilometers",
    "inches", "feet", "yards", "miles",
)

MSG_NOT_POSITIVE = "Please enter a number greater than zero."
MSG_INVALID = "Please enter a valid number."


def _all_widgets(widget):
    for child in widget.winfo_children():
        yield child
        yield from _all_widgets(child)


def _press(w, text, from_unit="inches", to_unit="millimeters"):
    w.entry.delete(0, "end")
    w.entry.insert(0, text)
    w.from_combo.set(from_unit)
    w.to_combo.set(to_unit)
    w.convert_button.invoke()
    return w.result_text()


# REQ-001
def test_req_001_window_has_required_widgets(window):
    root = window.entry.winfo_toplevel()
    widgets = list(_all_widgets(root))
    classes = [x.winfo_class() for x in widgets]
    assert classes.count("TEntry") == 1
    assert classes.count("TCombobox") == 2
    buttons = [x for x in widgets if x.winfo_class() == "TButton"]
    assert len(buttons) == 1
    assert str(buttons[0].cget("text")) == "Convert"
    results = [x for x in widgets if x.winfo_name() == "result"]
    assert len(results) == 1
    assert window.entry.winfo_name() == "amount"
    assert window.from_combo.winfo_name() == "from_unit"
    assert window.to_combo.winfo_name() == "to_unit"


def test_req_001_result_area_empty_on_open(window):
    assert window.result_text() == ""


# REQ-002 / REQ-003
def test_req_002_from_combo_values(window):
    assert tuple(map(str, window.from_combo["values"])) == EXPECTED_UNITS
    assert window.from_combo.get() == "millimeters"


def test_req_003_to_combo_values(window):
    assert tuple(map(str, window.to_combo["values"])) == EXPECTED_UNITS
    assert window.to_combo.get() == "millimeters"


# REQ-006
def test_req_006_convert_button_shows_two_decimals(window):
    assert _press(window, "1", "meters", "inches") == "39.37"
    assert _press(window, "5", "meters", "meters") == "5.00"
    assert _press(window, "100", "feet", "meters") == "30.48"
    assert _press(window, "1", "millimeters", "miles") == "0.00"


# REQ-007
def test_req_007_zero_shows_message(window):
    assert _press(window, "0") == MSG_NOT_POSITIVE
    assert _press(window, "0.0", "miles", "feet") == MSG_NOT_POSITIVE


# REQ-008
def test_req_008_negative_shows_message(window):
    assert _press(window, "-5") == MSG_NOT_POSITIVE
    assert _press(window, "-0.01", "kilometers", "yards") == MSG_NOT_POSITIVE


# REQ-009
def test_req_009_invalid_shows_message(window):
    assert _press(window, "") == MSG_INVALID
    assert _press(window, "abc") == MSG_INVALID
    assert _press(window, "12ft") == MSG_INVALID


def test_req_009_valid_after_error_replaces_message(window):
    assert _press(window, "abc") == MSG_INVALID
    assert _press(window, "1", "inches", "millimeters") == "25.40"
