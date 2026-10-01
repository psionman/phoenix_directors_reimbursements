"""Tkinter frame for displaying reimbursement output."""

import tkinter as tk
from tkinter import ttk

from clipboard import copy
from psiutils.constants import PAD
from psiutils.utilities import window_resize

from directors_reimbursements import logger
from directors_reimbursements.buttons import ButtonFrame
from directors_reimbursements.state import state
from directors_reimbursements.text import Text

txt = Text()


class OutputFrame:
    def __init__(self, parent: tk.Frame) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.output = self._enhance_output(parent.output)

        # tk Variables
        self.csv_report = tk.StringVar(value=self.output)

        self._show()

    def _show(self) -> None:
        root = self.root
        root.geometry(state.get_geometry(__file__))
        root.title(f"{txt.TITLE} -  Report")

        root.bind("<Control-x>", self._dismiss)
        root.bind("<Control-c>", self._copy)

        root.bind(
            "<Configure>",
            lambda e: window_resize(root, __file__, state),
        )

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(
            row=8, column=0, columnspan=9, sticky=tk.EW, padx=PAD, pady=PAD
        )

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_box = tk.Text(frame)
        output = [f"{item[0]:<10} {item[1]:>6}" for item in self.output]
        text_box.insert("1.0", "\n".join(output))
        text_box.grid(row=0, column=0, sticky=tk.NSEW)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button("copy-clipboard", self._copy),
            frame.icon_button("exit", self._dismiss),
        ]
        return frame

    def _copy(self, *args) -> None:
        logger.info("Copied output to clipboard")
        output = [f"{item[0]},{item[1]}" for item in self.output]
        copy("\n".join(output))

    def _enhance_output(self, names_output: list) -> None:
        dates = self.parent.dates
        date_str = (
            f"Directors reimbursement "
            f"{dates.start_date.strftime('%b')} - "
            f"{dates.end_date.strftime('%b')} "
            f"{dates.end_date.year}"
        )

        output = [(date_str, "")]

        output.append(("", "Opening balance"))
        output.extend((item[0], item[1]) for item in names_output)
        print(output)
        return output

    def _dismiss(self, *args):
        self.root.destroy()
