""" Constants to support the application."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir

from psiutils.known_paths import get_downloads_dir

# APP level data
APP_TITLE = 'Phoenix Bridge Club Director\'s Reimbursement'

APP_NAME = 'phoenix_directors_reimbursements'
APP_AUTHOR = 'psionman'
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), 'config.toml')
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
REPORTS_DIRECTORY = 'reports'
DOWNLOADS = get_downloads_dir()

# Application specific
AUTHOR = 'Jeff Watkins'
APP_TITLE = "Phoenix Director's Reimbursements"
ICON_FILE = Path(Path(__file__).parent, 'images/phoenix.png')

# Files and directories
WORKBOOK = 'directors-rota.xlsx'
EMAIL_TEMPLATE = Path(USER_DATA_DIR, 'reimbursement_email_template.txt')
EMAIL_FILE_PREFIX = 'emails'
DATA_DIR = 'data'
TXT_FILE_TYPES = (
    ('text files', '*.txt'),
    ('All files', '*.*')
)
XLS_FILE_TYPES = (
    ('xlsx files', '*.xlsx'),
    ('All files', '*.*')
)

# Sheet variables
SHEET_NAME = 'Main'

INITIALS_COL = 0
NAME_COL = 1
EMAIL_COL = 2
USERNAME_COL = 3
ACTIVE_COL = 4

MON_DATE_COL = 0
WED_DATE_COL = 3

DATE_FORMAT = '%d %b %Y'
MONTH_FORMAT = '%b %Y'
