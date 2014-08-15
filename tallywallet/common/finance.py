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

Amortization = namedtuple(
    "Amortization",
    ["date", "payment", "interest", "repaid", "balance"])


def discount_simple(note:Note):
    """
    Ref MoF Eqn 5.2
    Discounted value of an ordinary simple annuity.
    """
    n = int(note.term / note.period)
    i = note.interest * Decimal(note.period / datetime.timedelta(days=360))
    R = note.principal * i / (1 - (1 + i) ** -n)
    return (n, i, R)


def schedule(note:Note, places=2, rounding=decimal.ROUND_UP):
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
    return next(value_series(m=1, **vars(note)))[1]


def value_series(date, principal, term, period, interest, m=1, **kwargs):
    interval = min(term, period / m)
    rate = interest * Decimal(interval / period)
    t = date
    for i in range(term // interval):
        t += interval
        principal = principal * (1 + rate)
        yield (t, principal)
