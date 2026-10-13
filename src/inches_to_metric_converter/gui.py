"""Thin tkinter window around the conversion core."""
import tkinter
from tkinter import ttk

from . import core


class ConverterWindow:
    def __init__(self, root: tkinter.Misc) -> None:
        self.entry = ttk.Entry(root, name="amount")
        self.entry.grid(row=0, column=0, columnspan=2, padx=8, pady=4, sticky="ew")

        ttk.Label(root, text="From:").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self.from_combo = ttk.Combobox(root, name="from_unit", values=core.UNITS,
                                       state="readonly")
        self.from_combo.current(0)
        self.from_combo.grid(row=1, column=1, padx=8, pady=4, sticky="ew")

        ttk.Label(root, text="To:").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self.to_combo = ttk.Combobox(root, name="to_unit", values=core.UNITS,
                                     state="readonly")
        self.to_combo.current(0)
        self.to_combo.grid(row=2, column=1, padx=8, pady=4, sticky="ew")

        self.convert_button = ttk.Button(root, name="convert", text="Convert",
                                         command=self.on_convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, padx=8, pady=4)

        self.result_label = ttk.Label(root, name="result", text="")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=8, pady=4)

    def on_convert(self) -> None:
        self.result_label.configure(
            text=core.convert_text(self.entry.get(), self.from_combo.get(),
                                   self.to_combo.get())
        )

    def result_text(self) -> str:
        return str(self.result_label.cget("text"))


def main() -> None:
    root = tkinter.Tk()
    root.title("Distance Converter")
    ConverterWindow(root)
    root.mainloop()
