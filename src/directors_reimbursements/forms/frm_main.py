"""Main screen for Phoenix Director's payments."""

import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from dateutil import relativedelta
from dateutil.parser import parse as date_parse

from psiutils.constants import PAD, LARGE_FONT
from psiutils.buttons import ButtonFrame, IconButton
from psiutils.widgets import clickable_widget, separator_frame
from psiutils.utilities import window_resize, geometry

from directors_reimbursements.config import read_config
from directors_reimbursements.constants import MONTH_FORMAT, XLS_FILE_TYPES
from directors_reimbursements.common import get_period_dates
from directors_reimbursements.process import calculate
from directors_reimbursements.text import Text

from directors_reimbursements.forms.frm_report import ReportFrame
from directors_reimbursements.main_menu import MainMenu

txt = Text()
DateDelta = relativedelta.relativedelta


class MainFrame():
    """Define the frame."""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.start_date: datetime = datetime.now()
        self.config = read_config()

        # tk variables
        dates = get_period_dates(datetime.now())
        payment_month = dates.payment_date.strftime(MONTH_FORMAT)
        self.payment_month = tk.StringVar(value=payment_month)
        self.pay_months = tk.StringVar(value=self._pay_months())
        self.workbook_path = tk.StringVar(value=self.config.workbook_path)

        self.workbook_path.trace_add('write', self.on_workbook_path_change)

        self._show()

    def _show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.title(txt.TITLE)

        root.bind('<Control-q>', self._dismiss)
        root.bind('<Control-g>', self._process)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        main_menu = MainMenu(self)
        main_menu.create()

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        header = ttk.Label(root, text=txt.TITLE, font=LARGE_FONT)
        header.grid(row=0, column=0, columnspan=99, padx=PAD, pady=PAD)

        main_frame = self._main_frame(root)
        main_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=2, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        # pylint: disable=no-member)
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        row = 0
        # Widgets for month file.
        label = ttk.Label(frame, text='Payment month')
        label.grid(row=row, column=1, sticky=tk.SW, padx=PAD)

        row += 1
        prev_button = IconButton(
            frame, txt.PREVIOUS, 'previous', self.previous_period_click,)
        prev_button.grid(row=row, column=0, sticky=tk.E)
        clickable_widget(prev_button)

        month_entry = ttk.Entry(frame, textvariable=self.payment_month)
        month_entry.grid(
            row=row, column=1, columnspan=2, sticky=tk.EW, padx=PAD, pady=PAD)

        next_button = ttk.Button(frame, text='Next',
                                 command=self.next_period_click)

        next_button = IconButton(
            frame, txt.NEXT, 'next', self.next_period_click,)
        next_button.grid(row=row, column=3, sticky=tk.W)
        clickable_widget(next_button)

        row += 1
        label = ttk.Label(frame, textvariable=self.pay_months)
        label.grid(row=row, column=0, columnspan=2,
                   sticky=tk.W, padx=PAD, pady=PAD)

        row += 1
        pay = f'{self.config.payment_bbo:.2f}'
        label = ttk.Label(frame, text=f'The payment per session is: ${pay}')
        label.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=PAD)

        # Workbook
        row += 1
        separator = separator_frame(frame, 'Director\'s rota workbook')
        separator.grid(row=row, column=0, columnspan=4,
                       sticky=tk.EW, padx=PAD, pady=PAD)

        row += 1
        label = ttk.Label(frame, text="Director's rota workbook")
        label.grid(row=row, column=0, sticky=tk.E)
        workbook_file_name = ttk.Entry(frame, textvariable=self.workbook_path)
        workbook_file_name.grid(row=row, column=1, sticky=tk.EW,
                                padx=PAD, pady=PAD)

        select = IconButton(
            frame, txt.OPEN, 'open', self.get_workbook_path)
        select.grid(row=row, column=3, padx=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('build', self._process),
            frame.icon_button('close', self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _change_month(self, *args) -> None:
        self.pay_months.set(self._pay_months())

    def _pay_months(self, *args) -> str:
        payment_month = date_parse(self.payment_month.get())
        start_month = payment_month - DateDelta(months=3)
        end_month = payment_month - DateDelta(months=1)
        return (f'Process payments for '
                f'{start_month.strftime(MONTH_FORMAT)} to '
                f'{end_month.strftime(MONTH_FORMAT)}')

    def previous_period_click(self) -> None:
        """Get previous period."""
        payment_date = date_parse(self.payment_month.get())
        payment_date -= DateDelta(months=self.config.period_months)
        self._update_dates(payment_date)

    def next_period_click(self) -> None:
        """Get next period."""
        payment_date = date_parse(self.payment_month.get())
        payment_date += DateDelta(months=self.config.period_months)
        self._update_dates(payment_date)

    def _update_dates(self, payment_date: datetime.date) -> None:
        dates = get_period_dates(payment_date)
        payment_month = dates.payment_date.strftime(MONTH_FORMAT)
        self.payment_month.set(payment_month)
        self.pay_months.set(self._pay_months())

    def get_workbook_path(self) -> None:
        """Set the workbook path"""
        workbook_path = filedialog.askopenfilename(
            title='Workbook',
            initialdir=str(Path(self.workbook_path.get()).parent),
            initialfile=str(Path(self.workbook_path.get()).name),
            filetypes=XLS_FILE_TYPES
        )

        if workbook_path:
            self.workbook_path.set(workbook_path)
            self.config.workbook_path = workbook_path

    def on_workbook_path_change(self, *args) -> None:
        self.set_file_message()

    def set_file_message(self) -> None:
        # pylint: disable=no-member)
        message = ''
        config_text = 'Click on Menu > Defaults to define.'
        email_template = os.path.isfile(self.config.email_template)
        directors_rota = os.path.isfile(self.workbook_path.get())
        if not email_template and not directors_rota:
            message = (f'Director\'s rota and email template not valid. '
                       f'{config_text}')
        elif not email_template and not directors_rota:
            message = f'Email template not valid. {config_text}'
        elif not email_template and not directors_rota:
            message = 'Director\'s rota not valid.'
        if message:
            self.button_frame.enable(False)

    def _process(self, *args) -> None:
        payment_date = date_parse(self.payment_month.get())
        dates = get_period_dates(payment_date)

        (directors, formatted_report, csv_report) = calculate(dates)
        if formatted_report:
            dlg = ReportFrame(
                self, directors, formatted_report, csv_report, dates)
            self.root.wait_window(dlg.root)
            self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()
