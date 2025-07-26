import tkinter as tk
from tkinter import messagebox

from psiutils.menus import Menu, MenuItem
from psiutils.widgets import About

from config import config
from constants import AUTHOR, APP_TITLE, USER_DATA_DIR
import text
from _version import __version__

from forms.frm_config import ConfigFrame

SPACES = ' '*20


class MainMenu():
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self.config = config

    def create(self):
        menubar = tk.Menu()
        self.root['menu'] = menubar

        # File menu
        file_menu = Menu(menubar, self._file_menu_items())
        menubar.add_cascade(menu=file_menu, label='File')

        # Help menu
        help_menu = Menu(menubar, self._help_menu_items())
        menubar.add_cascade(menu=help_menu, label='Help')

    def _file_menu_items(self) -> list:
        return [
            # MenuItem(f'{CLUB_TEXT}{text.ELLIPSIS}', self._show_clubs_frame),
            # MenuItem(f'{COPY_PLAYERS_TEXT}{text.ELLIPSIS}',
            #          self._show_copy_players),
            MenuItem(f'{text.CONFIG}{text.ELLIPSIS}', self._show_config_frame),
            MenuItem(text.EXIT, self.dismiss),
        ]

    def _show_config_frame(self):
        """Display the config frame."""
        dlg = ConfigFrame(self)
        self.root.wait_window(dlg.root)

    def _help_menu_items(self) -> list:
        return [
            MenuItem(f'On line help{text.ELLIPSIS}', self._show_help),
            MenuItem(f'Data directory location{text.ELLIPSIS}',
                     self._show_data_directory),
            MenuItem(f'About{text.ELLIPSIS}', self._show_about),
            # MenuItem(f'About frame{text.ELLIPSIS}', self._show_about_frame),
        ]

    def _show_help(self):
        # webbrowser.open(HELP_URI)
        ...

    def _show_data_directory(self):
        dir = f'Data directory: {config.data_directory} {SPACES}'
        messagebox.showinfo(title='Data directory', message=dir)

    def _show_about(self):
        about_text = {
            'author': AUTHOR,
            'version': __version__,
        }
        dlg = About(
            self,
            app_name=APP_TITLE,
            about_text=about_text,
            parent_file=__file__,
            data_dir=USER_DATA_DIR)
        self.root.wait_window(dlg.root)

    def dismiss(self, *args):
        self.root.destroy()
