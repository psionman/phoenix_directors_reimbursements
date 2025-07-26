"""Utilities for Phoenix Director's payments."""

from typing import NamedTuple
from datetime import datetime
from dateutil import relativedelta

from config import config

date_delta = relativedelta.relativedelta


class Dates(NamedTuple):
    start_date: datetime.date
    end_date: datetime.date
    payment_date: datetime.date


def get_period_dates(today: datetime.date) -> Dates:
    payment_month = today.month
    period = config.period_months
    while (payment_month - config.period_start_month) % period != 0:
        payment_month -= 1

    payment_date = datetime(today.year, payment_month, 1)
    end_date = payment_date - date_delta(days=1)
    start_date = payment_date - date_delta(months=config.period_months)
    dates = Dates(
        start_date,
        end_date,
        payment_date
    )
    return dates
