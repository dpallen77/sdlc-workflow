import pathlib
import sys

import pytest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def window():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Tk not available (no display): {e}")
    from inches_to_metric_converter.gui import ConverterWindow

    root.withdraw()
    w = ConverterWindow(root)
    root.update_idletasks()
    yield w
    root.destroy()
