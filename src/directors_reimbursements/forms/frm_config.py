import os
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from psiutils.buttons import ButtonFrame, Button, IconButton
from psiutils.constants import PAD
from psiutils.widgets import clickable_widget, separator_frame
from psiutils.utilities import window_resize, geometry

from constants import TXT_FILE_TYPES, XLS_FILE_TYPES
import text

from config import read_config, save_config


class ConfigFrame():
    """ConfigFrame for Director's reimbursements."""
    def __init__(self, parent) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        config = read_config()
        self.config = config

        # tk variables
        self.send_emails = tk.BooleanVar(value=config.send_emails)
        self.emails_to_file = tk.BooleanVar(value=config.emails_to_file)
        self.email_file_prefix = tk.StringVar(value=config.email_file_prefix)
        self.data_directory = tk.StringVar(value=config.data_directory)
        self.email_template = tk.StringVar(value=config.email_template)
        self.email_subject = tk.StringVar(value=config.email_subject)
        self.period_start_month = tk.IntVar(value=config.period_start_month)
        self.payment_bbo = tk.DoubleVar(value=config.payment_bbo)
        self.period_months = tk.IntVar(value=config.period_months)
        self.workbook_path = tk.StringVar(value=config.workbook_path)

        self.send_emails.trace_add('write', self._enable_buttons)
        self.emails_to_file.trace_add('write', self._enable_buttons)
        self.email_file_prefix.trace_add('write', self._enable_buttons)
        self.data_directory.trace_add('write', self._enable_buttons)
        self.email_template.trace_add('write', self._enable_buttons)
        self.email_subject.trace_add('write', self._enable_buttons)
        self.period_start_month.trace_add('write', self._enable_buttons)
        self.payment_bbo.trace_add('write', self._enable_buttons)
        self.period_months.trace_add('write', self._enable_buttons)
        self.workbook_path.trace_add('write', self._enable_buttons)

        self.show()

    def show(self) -> None:
        root = self.root
        root.geometry(geometry(self.config, __file__))
        root.transient(self.parent.root)
        root.title(f'{text.TITLE} - {text.CONFIG}')

        root.bind('<Control-x>', self.dismiss)
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
        separator = separator_frame(frame, f'{text.DIRECTORS} rota workbook')
        separator.grid(row=workbook_row+0, column=0, columnspan=3,
                       sticky=tk.EW, padx=PAD, pady=PAD)
        workbook_file_name = ttk.Entry(frame, textvariable=self.workbook_path)
        workbook_file_name.grid(row=workbook_row+1, column=0, columnspan=2,
                                sticky=tk.EW, padx=PAD, pady=PAD)
        self.workbook_path.trace_add('write', self.on_workbook_path_change)

        select = IconButton(frame, text.OPEN, 'open', self._set_workbook_path)
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
            values=[x for x in range(1, 13)],
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

        button = IconButton(frame, text.OPEN, 'open', self._get_data_directory)
        button.grid(row=file_row+1, column=2, padx=PAD)

        label = ttk.Label(frame, text='Email template')
        label.grid(row=file_row+2, column=0, sticky=tk.E, padx=PAD, pady=PAD)

        entry = ttk.Entry(frame, textvariable=self.email_template)
        entry.grid(row=file_row+2, column=1, sticky=tk.EW)

        button = IconButton(frame, text.OPEN, 'open', self._get_email_template)
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
            frame.icon_button('exit', False, self.dismiss),
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
        message = ''
        config_text = 'Click on Menu > Defaults to define.'
        email_template = os.path.isfile(self.config.email_template)
        directors_rota = os.path.isfile(self.workbook_path.get())
        if not email_template and not directors_rota:
            message = (f'{text.DIRECTORS} rota and email template not valid. '
                       f'{config_text}')
        elif not email_template and not directors_rota:
            message = f'Email template not valid. {config_text}'
        elif not email_template and not directors_rota:
            message = f'{text.DIRECTORS} rota not valid.'
        if message:
            self.button_frame.enable(False)

    def _value_changed(self) -> bool:
        return (
            self.workbook_path.get() != self.config.workbook_path or
            self.send_emails.get() != self.config.send_emails or
            self.emails_to_file.get() != self.config.emails_to_file or
            self.email_file_prefix.get() != self.config.email_file_prefix or
            self.data_directory.get() != self.config.data_directory or
            self.email_template.get() != str(self.config.email_template) or
            self.email_subject.get() != self.config.email_subject or
            self.period_start_month.get() != self.config.period_start_month or
            self.payment_bbo.get() != self.config.payment_bbo or
            self.period_months.get() != self.config.period_months
            )

    def _enable_buttons(self, *args) -> None:
        enable = False
        if self._value_changed():
            enable = True
        self.button_frame.enable(enable)

    def _save_config(self, *args) -> int:
        self.config.config['send_emails'] = self.send_emails.get()
        self.config.config['emails_to_file'] = self.emails_to_file.get()
        self.config.config['email_file_prefix'] = self.email_file_prefix.get()
        self.config.config['data_directory'] = self.data_directory.get()
        self.config.config['email_template'] = self.email_template.get()
        self.config.config['email_subject'] = self.email_subject.get()
        self.config.config['period_start_month'] = self.period_start_month.get()
        self.config.config['payment_bbo'] = self.payment_bbo.get()
        self.config.config['period_months'] = self.period_months.get()
        self.config.config['workbook_path'] = self.workbook_path.get()

        result = save_config(self.config)
        self.button_frame.enable(False)
        return result

    def dismiss(self, *args) -> None:
        self.root.destroy()
