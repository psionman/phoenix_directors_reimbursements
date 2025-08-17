"""Send and or save emails."""

from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTPAuthenticationError
import smtplib

from psiutils.errors import ErrorMsg
from psiutils.utilities import logger

from directors_reimbursements.constants import USER_DATA_DIR, DATE_FORMAT
from directors_reimbursements.process import Director
from directors_reimbursements.config import read_config, env


def send_emails(start_date: datetime,
                directors: dict[Director]) -> int | ErrorMsg:
    """Send Emails for the directors."""
    config = read_config()
    template = _email_template(config.email_template)
    if isinstance(template, ErrorMsg):
        return template

    emails_sent = 0
    for key, director in directors.items():
        if key and director.dollars > 0:
            print(director.email)
            response = _create_email(
                template, director, start_date, config.email_subject)
            if isinstance(response, ErrorMsg):
                return response
            emails_sent += 1
    return emails_sent


def _email_template(email_template_path: str) -> str | ErrorMsg:
    email_template = Path(USER_DATA_DIR, email_template_path)
    template = _get_email_template(email_template)
    if not template:
        return ErrorMsg(
            header='File error',
            message=f'Email template not found at: {email_template}.',
        )
    return template


def _get_email_template(email_template: Path) -> str:
    try:
        with open(email_template, 'r', encoding='utf-8') as f_email_text:
            return f_email_text.read()
    except (FileNotFoundError, NotADirectoryError):
        logger.error(f"Email template not found at {email_template}")
        return ''


def _create_email(
        base_content: str,
        director: Director,
        start_date: datetime,
        email_subject: str,
        ) -> str:
    body = _email_body(base_content, director, start_date)
    try:
        _send_email(
            email_subject,
            body,
            director.email,)
    except SMTPAuthenticationError:
        logger.error('Email authentication error.')
        return ErrorMsg(
            header='Email error',
            message='Email authentication error.',
        )
    except TypeError:
        logger.error('Email setup error.')
        return ErrorMsg(
            header='Email error',
            message='Email setup error.',
        )
    return True


def _email_body(base_content: str, director: Director,
                start_date: datetime) -> str:
    content = base_content
    content = content.replace('<first name>', director.first_name)
    content = content.replace('<dollars>', str(director.dollars))
    content = content.replace(
        '<period>', start_date.strftime(DATE_FORMAT))
    return content.replace('<dates>', ', '.join(director.dates))


def _send_email(subject, body, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = env['email_sender']
    msg['To'] = recipient
    # recipient = env['email_sender']
    with smtplib.SMTP_SSL(env['smtp_server'], env['smtp_port']) as smtp_server:
        smtp_server.login(env['email_sender'], env['email_key'])
        smtp_server.sendmail(env['email_sender'], recipient, msg.as_string())
    logger.info(f"Email sent to {recipient}")


def emails_to_file(
        start_date: datetime, directors: dict[Director]) -> int | ErrorMsg:
    """Send Emails for the directors to file."""
    # pylint: disable=no-member)
    config = read_config()
    template = _email_template(config.email_template)
    if isinstance(template, ErrorMsg):
        return template

    output = ''.join(
        _email_as_text(template, director, start_date, config.email_subject)
        for key, director in directors.items()
        if key and director.dollars > 0
    )
    date_str = datetime.now().strftime("%Y%m%d")
    email_file = Path(
        USER_DATA_DIR,
        'emails',
        f'{config.email_file_prefix}_{date_str}.txt')
    response = _save_emails(email_file, output)
    if not response:
        return ErrorMsg(
            header='File error',
            message=f'Emails not saved: {email_file}.',
        )
    return True


def _email_as_text(
        base_content: str,
        director: Director,
        start_date: datetime,
        email_subject: str,
        ) -> str:
    body = _email_body(base_content, director, start_date)
    output = (f'{director.email}\n'
              f'{email_subject}\n\n'
              f'{body}\n'
              f'{"-"*50}\n\n')
    return output


def _save_emails(email_file: Path, output: str) -> None:
    try:
        email_file.parent.mkdir(parents=True, exist_ok=True)
        with open(email_file, 'w') as f_email:
            f_email.write(output)
    except FileExistsError:
        pass
    except FileNotFoundError:
        return False
    return True
