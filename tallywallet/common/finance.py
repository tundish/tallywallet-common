#!/usr/bin/env python3.4
#   encoding: UTF-8

# This file is part of tallywallet.
#
# Tallywallet is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tallywallet is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with tallywallet.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
import datetime
import decimal
from decimal import Decimal

Note = namedtuple(
    "Note",
    ["date", "principal", "currency", "term", "interest", "period"])
Note.__doc__ = """`{}`

A Note keeps all the details of a promise to pay a debt,
as follows:

    date
        The date on which the loan is agreed.
    principal
        The amount of the original loan.
    currency
        The currency in which the loan will be paid.
    term
        The duration of the loan.
    interest
        The rate of interest.
    period
        The period of time over which interest is calculated.
""".format(Note.__doc__)

Amortization = namedtuple(
    "Amortization",
    ["date", "payment", "interest", "repaid", "balance"])
Amortization.__doc__ = """`{}`

An Amortization object records a payment against an amortization schedule:

    date
        The date on which the payment is made.
    payment
        The total amount of the payment.
    interest
        The amount paid as interest.
    repaid
        The amount repaid from the principal.
    balance
        The remaining balance of the loan.
""".format(Amortization.__doc__)


def discount_simple(note:Note):
    """
    Calculates the discounted value of an ordinary simple annuity.
    See `Schaum's Mathematics of Finance` Equation 5.2 .

    Returns a 3-tuple of (number of payments, annualised rate, annuity payment)
 
    """
    n = int(note.term / note.period)
    i = note.interest * Decimal(note.period / datetime.timedelta(days=360))
    R = note.principal * i / (1 - (1 + i) ** -n)
    return (n, i, R)


def schedule(note:Note, places=2, rounding=decimal.ROUND_UP):
    """
    Calculate the amortization schedule for a
    :py:class:`Note <tallywallet.common.finance.Note>`.

    places
        An integer. Round the balance to this number of decimal places
        at each calculation interval.
    rounding
        Selects the rounding method. Must be one of the constants defined
        for this purpose in the `decimal` standard library module.

    This function is a generator. It produces a sequence of
    :py:class:`Amortization <tallywallet.common.finance.Amortization>`
    objects.
    """
    quantum = Decimal(10) ** -places
    n, rate, annuity = discount_simple(note)
    payment = annuity.quantize(quantum, rounding=rounding)
    balance = note.principal
    end = note.date + note.term
    ts = note.date
    while ts < end:
        ts += note.period
        interest = rate * balance
        payment = min(balance + interest, payment)
        repaid = payment - interest
        balance -= repaid
        yield Amortization(ts, payment, interest, repaid, balance)


def value_simple(note:Note):
    """
    Returns the simple value of a promissory note on maturity.
    """
    return next(value_series(m=1, **vars(note)))[1]


def value_series(date, principal, term, period, interest, m=1, **kwargs):
    """
    Calculate the value of a debt over time. Parameters are as for the
    :py:class:`Note <tallywallet.common.finance.Note>` type. Additionally:

    m
        The number of times per `period` that interest is compounded.

    This function is a generator. It produces 2-tuples of (date, value).
    """
    interval = min(term, period / m)
    rate = interest * Decimal(interval / period)
    t = date
    for i in range(term // interval):
        t += interval
        principal = principal * (1 + rate)
        yield (t, principal)
