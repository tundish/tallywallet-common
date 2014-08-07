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

import datetime
import decimal
from decimal import ROUND_05UP
import fractions
import itertools
import unittest

#prototyping
from collections import namedtuple
from decimal import Decimal

Note = namedtuple("Note", ["date", "principal", "currency", "term", "interest", "period"])
Schedule = namedtuple("Schedule", ["n", "val"])

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


class FinancialEvents(unittest.TestCase):

    def test_loan_book(self):
        now = datetime.datetime.utcnow()
        then = now + datetime.timedelta(weeks=104)
        asset = Note(now, 1000, "GBP", then - now, Decimal("0.06"),
                     datetime.timedelta(days=60))
        print(list(value_series(**vars(asset))))

class ProgressionTests(unittest.TestCase):

    def test_arithmetic_progression(self):
        """MoF 2Ed 2.1"""
        proc = (
            Schedule(n, v) for n, v in enumerate(itertools.count(-1, 3)))
        prog = list(itertools.takewhile(lambda i: i.n < 15, proc))
        self.assertEqual(41, prog[-1].val)
        self.assertEqual(300, sum(i.val for i in prog))


class TestCompoundInterest(unittest.TestCase):

    def test_value_series(self):
        """Schaum's MoF 2Ed 4.1"""
        note = Note(
            date=datetime.date(2012, 7, 30),
            principal=1000,
            currency=None,
            term=datetime.timedelta(days=720),
            interest=Decimal("0.12"),
            period=datetime.timedelta(days=360)
        )
        series = list(value_series(m=2, **vars(note)))
        self.assertEqual(4, len(series))
        # NB: Pennies are off-by-one from reference ->     ¬          ¬ 
        self.assertEqual(
            [Decimal(i) for i in ("1060", "1123.6", "1191.01", "1262.47")],
            [i[1].quantize(Decimal("0.01"), rounding=ROUND_05UP)
                for i in series]
        )


class TestPromissoryNote(unittest.TestCase):

    def test_value_simple(self):
        """Schaum's MoF 2Ed 3.29"""
        note = Note(
            date=datetime.date(1995, 5, 11),
            principal=1500,
            currency=None,
            term=datetime.timedelta(days=90),
            interest=Decimal("0.08"),
            period=datetime.timedelta(days=360)
        )
        self.assertEqual(
            Decimal("1530.00"),
            value_simple(note)
        )

    def test_sale_at_discount(self):
        """Schaum's MoF 2Ed 3.30"""
        note = Note(
            date=datetime.date(1995, 5, 11),
            principal=1500,
            currency=None,
            term=datetime.timedelta(days=90),
            interest=Decimal("0.08"),
            period=datetime.timedelta(days=360)
        )
        valueAtMaturity = value_simple(note)
        self.assertEqual(1530, valueAtMaturity)

        dateOfSale = datetime.date(1995, 7, 2)
        termRemaining = note.date + note.term - dateOfSale
        self.assertEqual(38, termRemaining.days)
        _, valueAtDiscount = next(value_series(
            date=note.date + note.term,
            principal=valueAtMaturity, term=(-termRemaining),
            period=note.period, interest=Decimal("0.09")))
        self.assertEqual(
            Decimal("1515.46"),
            valueAtDiscount.quantize(Decimal("0.01"), rounding=ROUND_05UP)
        )
