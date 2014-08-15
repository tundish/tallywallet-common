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
from decimal import Decimal
import unittest

from tallywallet.common.finance import Amortization
from tallywallet.common.finance import Note
from tallywallet.common.finance import discount_simple
from tallywallet.common.finance import schedule
from tallywallet.common.finance import value_series
from tallywallet.common.finance import value_simple

class AmortizationTests(unittest.TestCase):

    def test_loan_payment(self):
        """
        MoF 2Ed 7.1

        A debt of $6000 with interest at 16% compounded semiannually is
        to be amortized by equal semiannual payments of $R over the next 3
        years, the first payment due in 6 months.

        Find the payment rounded up to the nearest cent.

        """
        now = datetime.datetime.utcnow()
        loan = Note(
            now, 6000, "USD",
            datetime.timedelta(days=360*3),
            Decimal("0.16"), datetime.timedelta(days=180))

        R = discount_simple(loan)[2]
        self.assertEqual(
            Decimal("1297.90"),
            R.quantize(Decimal("0.01"), rounding=decimal.ROUND_UP)
        )

    def test_amortization_schedule(self):
        """
        MoF 2Ed 7.4

        A debt of $6000 with interest at 16% compounded semiannually is
        to be amortized by equal semiannual payments of $R over the next 3
        years, the first payment due in 6 months.

        Construct a complete amortization schedule for the debt.

        """
        now = datetime.datetime.utcnow()
        loan = Note(
            now, 6000, "USD",
            datetime.timedelta(days=360*3),
            Decimal("0.16"), datetime.timedelta(days=180))

        record = list(schedule(loan, places=0))

        self.assertEqual(6, len(record))
        self.assertEqual(
            Decimal("7787.21"),
            sum(i.payment for i in record).quantize(Decimal("0.01"))
        )
        self.assertEqual(
            Decimal("1787.21"),
            sum(i.interest for i in record).quantize(Decimal("0.01"))
        )
        self.assertEqual(6000, sum(i.repaid for i in record))
        self.assertEqual(0, record[-1].balance)


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
            [i[1].quantize(Decimal("0.01"), rounding=decimal.ROUND_05UP)
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
            valueAtDiscount.quantize(
                Decimal("0.01"), rounding=decimal.ROUND_05UP)
        )
