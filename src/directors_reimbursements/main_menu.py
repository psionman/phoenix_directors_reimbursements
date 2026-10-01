import tkinter as tk
from tkinter import messagebox

from psiutils.menus import Menu, MenuItem

from directors_reimbursements import (
    __app_name__,
    __author__,
    __summary__,
    __version__,
)
from directors_reimbursements.config import config
from directors_reimbursements.forms.frm_config import ConfigFrame
from directors_reimbursements.text import Text

txt = Text()

SPACES = 30
SEPARATOR = "-" * 50


class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self.config = config

    def create(self):
        menubar = tk.Menu()
        self.root["menu"] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label="File")

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label="Help")

    def _file_menu_items(self) -> list:
        return [
            MenuItem(f"{txt.CONFIG}{txt.ELLIPSIS}", self._show_config_frame),
            MenuItem(txt.EXIT, self.dismiss),
        ]

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        dlg.root.transient(self.root)
        dlg.root.grab_set()
        self.root.wait_window(dlg.root)

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f"On line help{txt.ELLIPSIS}", self._show_help),
            MenuItem(
                f"Data directory location{txt.ELLIPSIS}",
                self._show_data_directory,
            ),
            MenuItem(f"About{txt.ELLIPSIS}", self._show_about),
        ]

    def _show_help(self):
        # webbrowser.open(HELP_URI)
        ...

    def _show_data_directory(self):
        msg = f"Data directory: {config.data_directory} {SPACES}"
        messagebox.showinfo(title="Data directory", message=msg)

    def _show_about(self):
        about = (
            f"{__summary__}\n"
            f"{SEPARATOR}\n"
            f"{txt.VERSION}: {__version__}\n"
            f"{SEPARATOR}\n"
            f"{txt.AUTHOR}: {__author__:<{SPACES}}"
        )
        messagebox.showinfo(title=f"{txt.ABOUT} {__app_name__}", message=about)

    def dismiss(self, *args):
        self.root.destroy()
