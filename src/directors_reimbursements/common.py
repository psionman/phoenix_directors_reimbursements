"""Utilities for Phoenix Director's payments."""

from typing import NamedTuple
from datetime import datetime
from dateutil import relativedelta

from directors_reimbursements.config import config

DateDelta = relativedelta.relativedelta


class Dates(NamedTuple):
    """Period dates as an object."""
    start_date: datetime.date
    end_date: datetime.date
    payment_date: datetime.date


def get_period_dates(today: datetime.date) -> Dates:
    """Return period dates as a Dates object."""
    # pylint: disable=no-member)
    payment_month = today.month
    period = config.period_months
    while (payment_month - config.period_start_month) % period != 0:
        payment_month -= 1

    payment_date = datetime(today.year, payment_month, 1)
    end_date = payment_date - DateDelta(days=1)
    start_date = payment_date - DateDelta(months=config.period_months)
    return Dates(start_date, end_date, payment_date)
