"""Constants to support the application."""

from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_state_dir
from psiutils.known_paths import get_downloads_dir

from directors_reimbursements import __app_name__, __author__

# Paths
CONFIG_PATH = Path(user_config_dir(__app_name__, __author__), "config.toml")
USER_DATA_DIR = Path(user_data_dir(__app_name__, __author__))
REPORTS_DIRECTORY = "reports"
DOWNLOADS = get_downloads_dir()
STATE_DIR = user_state_dir(__app_name__, __author__)

# Application specific
ICON_FILE = Path(Path(__file__).parent, "images", "icon.png")

# Files and directories
WORKBOOK = "directors-rota.xlsx"
EMAIL_TEMPLATE = Path(USER_DATA_DIR, "reimbursement_email_template.txt")
EMAIL_FILE_PREFIX = "emails"
DATA_DIR = "data"
TXT_FILE_TYPES = (("text files", "*.txt"), ("All files", "*.*"))
XLS_FILE_TYPES = (("xlsx files", "*.xlsx"), ("All files", "*.*"))

# Buttons and text
PSIUTILS_DIR = user_data_dir("psiutils", __author__)
BUTTONS_DIR = Path(PSIUTILS_DIR, "buttons")
BUTTON_ICON_PATH = str(Path(BUTTONS_DIR, "icons"))
BUTTON_CONFIG_PATH = str(Path(BUTTONS_DIR, "buttons.json"))
TEXT_FILE = Path(PSIUTILS_DIR, "text", "text.json")

# GUI
APP_TITLE = "Directors Reimbursements"
ICON_FILE = Path(Path(__file__).parent, "images", "icon.png")

# Sheet variables
SHEET_NAME = "Main"

INITIALS_COL = 0
NAME_COL = 1
EMAIL_COL = 2
USERNAME_COL = 3
ACTIVE_COL = 4

MON_DATE_COL = 0
WED_DATE_COL = 3
THU_DATE_COL = 6

DATE_FORMAT = "%d %b %Y"
MONTH_FORMAT = "%b %Y"
