import os
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from psiutils.buttons import ButtonFrame, IconButton
from psiutils.constants import PAD
from psiutils.widgets import clickable_widget, separator_frame
from psiutils.utilities import window_resize, geometry, logger

from directors_reimbursements.constants import TXT_FILE_TYPES, XLS_FILE_TYPES
from directors_reimbursements.config import read_config
from directors_reimbursements import text as txt

FIELDS = {
    "send_emails": tk.BooleanVar,
    "emails_to_file": tk.BooleanVar,
    "email_file_prefix": tk.StringVar,
    "data_directory": tk.StringVar,
    "email_template": tk.StringVar,
    "email_subject": tk.StringVar,
    "period_start_month": tk.IntVar,
    "payment_bbo": tk.DoubleVar,
    "period_months": tk.IntVar,
    "workbook_path": tk.StringVar,
}


class ConfigFrame():
    """ConfigFrame for Director's reimbursements."""

    send_emails: tk.BooleanVar
    emails_to_file: tk.BooleanVar
    email_file_prefix: tk.StringVar
    data_directory: tk.StringVar
    email_template: tk.StringVar
    email_subject: tk.StringVar
    period_start_month: tk.IntVar
    payment_bbo: tk.DoubleVar
    period_months: tk.IntVar
    workbook_path: tk.StringVar
    def __init__(self, parent) -> None:
        # pylint: disable=no-member)
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        config = read_config()
        self.config = config

        # tk variables

        for field, f_type in FIELDS.items():
            if f_type is tk.StringVar:
                setattr(self, field, self._stringvar(getattr(config, field)))
            elif f_type is tk.IntVar:
                setattr(self, field, self._intvar(getattr(config, field)))
            elif f_type is tk.DoubleVar:
                setattr(self, field, self._doublevar(getattr(config, field)))
            elif f_type is tk.BooleanVar:
                setattr(self, field, self._boolvar(getattr(config, field)))

        self._show()

    def _stringvar(self, value: str) -> tk.StringVar:
        stringvar = tk.StringVar(value=value)
        stringvar.trace_add('write', self._check_value_changed)
        return stringvar

    def _intvar(self, value: int) -> tk.IntVar:
        intvar = tk.IntVar(value=value)
        intvar.trace_add('write', self._check_value_changed)
        return intvar

    def _doublevar(self, value: int) -> tk.IntVar:
        doublevar = tk.DoubleVar(value=value)
        doublevar.trace_add('write', self._check_value_changed)
        return doublevar

    def _boolvar(self, value: bool) -> tk.BooleanVar:
        boolvar = tk.BooleanVar(value=value)
        boolvar.trace_add('write', self._check_value_changed)
        return boolvar

    def _show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.transient(self.parent.root)
        root.title(f'{txt.TITLE} - {txt.CONFIG}')

        root.bind('<Control-x>', self._dismiss)
        root.bind('<Control-s>', self._save_config)
        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=99, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # Workbook
        workbook_row = 0
        separator = separator_frame(frame, f'{txt.DIRECTORS} rota workbook')
        separator.grid(row=workbook_row+0, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD, pady=PAD)
        workbook_file_name = ttk.Entry(frame, textvariable=self.workbook_path)
        workbook_file_name.grid(row=workbook_row+1, column=0, columnspan=2,
                                sticky=tk.EW, padx=PAD, pady=PAD)
        self.workbook_path.trace_add('write', self.on_workbook_path_change)

        select = IconButton(frame, txt.OPEN, 'open', self._set_workbook_path)
        select.grid(row=workbook_row+1, column=2)
        clickable_widget(select)

        # Payments
        payment_row = 2
        separator = separator_frame(frame, 'Payment details')
        separator.grid(row=payment_row+0, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='Period start month')
        label.grid(row=payment_row+1, column=0,
                   sticky=tk.E, padx=PAD, pady=PAD)

        combobox = ttk.Combobox(
            frame,
            textvariable=self.period_start_month,
            values=list(range(1, 13)),
            )
        combobox.grid(row=payment_row+1, column=1, sticky=tk.W)
        clickable_widget(combobox)

        label = ttk.Label(frame, text='Session payment ($)')
        label.grid(row=payment_row+2, column=0,
                   sticky=tk.E, padx=PAD, pady=PAD)

        spinbox = ttk.Spinbox(
            frame,
            format='%.2f',
            from_=0.5,
            to=100,
            increment=0.5,
            textvariable=self.payment_bbo)
        spinbox.grid(row=payment_row+2, column=1, sticky=tk.W)
        clickable_widget(spinbox)

        label = ttk.Label(frame, text='Period months')
        label.grid(row=payment_row+3, column=0,
                   sticky=tk.E, padx=PAD, pady=PAD)

        combobox = ttk.Combobox(
            frame,
            textvariable=self.period_months,
            values=[1, 2, 3, 4, 6, 12],
            )
        combobox.grid(row=payment_row+3, column=1, sticky=tk.W)
        clickable_widget(combobox)

        # File details
        file_row = 6
        separator = separator_frame(frame, 'Email preferences')
        separator.grid(row=file_row+0, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD, pady=PAD)

        label = ttk.Label(frame, text='Directory to store emails')
        label.grid(row=file_row+1, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.data_directory)
        entry.grid(row=file_row+1, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, 'open', self._get_data_directory)
        button.grid(row=file_row+1, column=2, padx=PAD)

        label = ttk.Label(frame, text='Email template')
        label.grid(row=file_row+2, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.email_template)
        entry.grid(row=file_row+2, column=1, sticky=tk.EW)

        button = IconButton(frame, txt.OPEN, 'open', self._get_email_template)
        button.grid(row=file_row+2, column=2, padx=PAD, pady=PAD)

        check_button = tk.Checkbutton(frame, text='Send emails',
                                      variable=self.send_emails)
        check_button.grid(row=file_row+3, column=0, sticky=tk.W)

        check_button = tk.Checkbutton(frame, text='Emails to file',
                                      variable=self.emails_to_file)
        check_button.grid(row=file_row+4, column=0, sticky=tk.W)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ButtonFrame(master, tk.HORIZONTAL)
        frame.buttons = [
            frame.icon_button('save', True, self._save_config),
            frame.icon_button('exit', False, self._dismiss),
        ]
        frame.enable(False)
        return frame

    def _get_data_directory(self) -> str:
        directory = filedialog.askdirectory(
            title='Data Directory',
            initialdir=self.data_directory.get(),
            parent=self.root,
        )
        if not directory:
            return
        self.data_directory.set(directory)
        return directory

    def _get_email_template(self) -> str:
        """Return a path to a file."""
        path = filedialog.askopenfilename(
            title='Email template',
            initialfile=self.email_template.get(),
            parent=self.root,
            filetypes=TXT_FILE_TYPES
        )
        if not path:
            return
        self.email_template.set(path)
        return path

    def _set_workbook_path(self) -> None:
        """Set the workbook path."""
        workbook_file_name = filedialog.askopenfilename(
            title='Workbook',
            initialdir=str(Path(self.workbook_path.get()).parent),
            initialfile=str(Path(self.workbook_path.get()).name),
            filetypes=XLS_FILE_TYPES
        )

        if workbook_file_name:
            self.workbook_path.set(workbook_file_name)
            self.config.workbook_file_name = workbook_file_name

    def on_workbook_path_change(self, *args) -> None:
        self.set_file_message()

    def set_file_message(self) -> None:
        # pylint: disable=no-member)
        message = ''
        email_template = os.path.isfile(self.config.email_template)
        directors_rota = os.path.isfile(self.workbook_path.get())
        config_text = 'Click on Menu > Defaults to define.'
        if not email_template and not directors_rota:
            message = (f'{txt.DIRECTORS} rota and email template not valid. '
                       f'{config_text}')
        elif not email_template and not directors_rota:
            message = f'Email template not valid. {config_text}'
        elif not email_template and not directors_rota:
            message = f'{txt.DIRECTORS} rota not valid.'
        if message:
            self.button_frame.enable(False)

    def _check_value_changed(self, *args) -> bool:
        """
        Enable or disable form buttons based on changes in configuration.
        """
        enable = bool(self._config_changes())
        self.button_frame.enable(enable)

    def _save_config(self):
        changes = {field: f'(old value={change[0]}, new_value={change[1]})'
                   for field, change in self._config_changes().items()}

        logger.info(
            "Config saved",
            changes=changes
        )

        for field in FIELDS:
            self.config.config[field] = getattr(self, field).get()
        return self.config.save()

    def _config_changes(self) -> dict:
        stored = self.config.config
        return {
            field: (stored[field], getattr(self, field).get())
            for field in FIELDS
            if stored[field] != getattr(self, field).get()
        }

    def _dismiss(self, *args) -> None:
        self.root.destroy()
