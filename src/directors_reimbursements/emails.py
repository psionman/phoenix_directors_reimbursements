"""Send and or save emails."""

from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from smtplib import SMTPAuthenticationError
import smtplib

from psiutils.errors import ErrorMsg

from constants import USER_DATA_DIR, DATE_FORMAT
from process import Director
from config import read_config, env


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
        with open(email_template, 'r') as f_email_text:
            template = f_email_text.read()
            return template
    except FileNotFoundError:
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
        return ErrorMsg(
            header='Email error',
            message='Email authentication error.',
        )
    except TypeError:
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
    content = content.replace('<dates>', ', '.join(director.dates))
    return content


def _send_email(subject, body, recipient):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = env['email_sender']
    msg['To'] = recipient
    # recipient = env['email_sender']
    with smtplib.SMTP_SSL(env['smtp_server'], env['smtp_port']) as smtp_server:
        smtp_server.login(env['email_sender'], env['email_key'])
        smtp_server.sendmail(env['email_sender'], recipient, msg.as_string())


def emails_to_file(
        start_date: datetime, directors: dict[Director]) -> int | ErrorMsg:
    """Send Emails for the directors to file."""
    config = read_config()
    template = _email_template(config.email_template)
    if isinstance(template, ErrorMsg):
        return template

    output = ''
    for key, director in directors.items():
        if key and director.dollars > 0:
            output += _email_as_text(
                template, director, start_date, config.email_subject)

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
