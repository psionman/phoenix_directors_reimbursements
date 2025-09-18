"""Tkinter frame for displaying reimbursement report."""

import tkinter as tk
from tkinter import ttk, messagebox
from clipboard import copy

from psiutils.constants import PAD
from psiutils.errors import ErrorMsg
from psiutils.buttons import ButtonFrame
from psiutils.widgets import WaitCursor
from psiutils.utilities import window_resize, geometry

from directors_reimbursements.emails import send_emails, emails_to_file
from directors_reimbursements.common import Dates
from directors_reimbursements.config import read_config
from directors_reimbursements.text import Text
from directors_reimbursements import logger

txt = Text(1)


class ReportFrame():
    def __init__(self, parent: tk.Frame,
                 directors: dict,
                 formatted_report: list,
                 csv_report: list,
                 dates: Dates) -> None:
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.formatted_report = formatted_report
        self.csv_report = csv_report
        self.directors = directors
        self.dates = dates
        self.config = read_config()

        # tk Variables
        self.send_emails = tk.BooleanVar(value=self.config.send_emails)
        self.emails_to_file = tk.BooleanVar(value=self.config.emails_to_file)

        self.send_emails.trace_add('write', self._check_button_enable)
        self.emails_to_file.trace_add('write', self._check_button_enable)

        self._show()
        self._enable_buttons()

    def _show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(f'{txt.TITLE} -  Report')

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-c>', self._copy)
        root.bind('<Control-e>', self._emails)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        options_frame = self._options_frame(root)
        options_frame.grid(row=1, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_box = tk.Text(frame, height=20)
        text_box.insert('1.0', '\n'.join(self.formatted_report))
        text_box.grid(row=0, column=0, sticky=tk.NSEW)

        return frame

    def _options_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)

        check_button = tk.Checkbutton(frame, text='Send emails',
                                      variable=self.send_emails)
        check_button.grid(row=0, column=0)

        check_button = tk.Checkbutton(frame, text='Save emails in file',
                                      variable=self.emails_to_file)
        check_button.grid(row=0, column=1)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('send', self._emails),
            frame.icon_button('copy_clipboard', self._copy),
            frame.icon_button('exit', self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _emails(self, *args) -> None:
        with WaitCursor(self.root):

            if self.emails_to_file.get():
                response = emails_to_file(
                    self.parent.start_date, self.directors)
                if isinstance(response, ErrorMsg):
                    response.show_message(self.root)
                    self.root.config(cursor='')
                    return

            if self.send_emails.get():
                response = send_emails(self.dates.start_date, self.directors)
                if isinstance(response, ErrorMsg):
                    response.show_message(self.root)
                    self.root.config(cursor='')
                    return
                messagebox .showinfo(
                    'Emails', f'{response} emails sent.', parent=self.root)
            self.root.config(cursor='')

    def _copy(self, *args) -> None:
        logger.info("Copied csv report to clipboard")
        copy('\n'.join(self.csv_report))

    def _check_button_enable(self) -> None:
        self._enable_buttons()

    def _enable_buttons(self) -> None:
        self.button_frame.enable(False)
        if self.send_emails.get() or self.emails_to_file.get():
            self.button_frame.enable(True)

    def _dismiss(self, *args):
        self.root.destroy()
