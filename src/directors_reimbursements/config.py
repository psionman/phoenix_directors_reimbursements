"""Config for Phoenix Director's payments."""
import os
from pathlib import Path

from psiconfig import TomlConfig
from constants import CONFIG_PATH, DOWNLOADS, USER_DATA_DIR
from dotenv import load_dotenv


DEFAULT_CONFIG = {
    'send_emails': True,
    'emails_to_file': True,
    'email_file_prefix': 'emails',
    'data_directory': USER_DATA_DIR,
    'email_template': Path(USER_DATA_DIR, 'reimbursement_email_template.txt'),
    'email_subject': 'Phoenix Bridge Club - Director\'s playing fees',
    'period_start_month': 1,
    'payment_bbo':  3,
    'period_months':  3,
    'workbook_path': Path(DOWNLOADS, 'directors-rota.xlsx'),
    'geometry': {}
}


def read_config() -> TomlConfig:
    """Return the config file."""
    config = TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)
    config.period_months = int(config.period_months)

    return config


def save_config(config: TomlConfig) -> TomlConfig | None:
    result = config.save()
    if result != config.STATUS_OK:
        return None
    config = TomlConfig(CONFIG_PATH)
    return config


def _get_env() -> dict:
    load_dotenv()
    try:
        smtp_port = int(os.getenv('SMTP_PORT'))
    except TypeError:
        smtp_port = 0

    return {
        'email_key': os.getenv('EMAIL_KEY'),
        'email_sender': os.getenv('EMAIL_SENDER'),
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': smtp_port
    }


config = read_config()
env = _get_env()
