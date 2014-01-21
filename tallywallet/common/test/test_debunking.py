#!/usr/bin/env python3
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

from decimal import Decimal
from decimal import ROUND_UP
import unittest
import unittest as functest

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.debunking import *
from tallywallet.common.exchange import Exchange
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role


class DebunkingTests(unittest.TestCase):

    def setUp(self):
        self.ldgr = Ledger(*columns.values(), ref=Cy.USD)

    def test_loan(self):
        cap = int(1E6)
        self.ldgr.commit(cap, columns["vault"])
        val = bank_loan(self.ldgr, YEAR)
        self.assertEqual(cap-val, self.ldgr.value("vault"))
        self.assertEqual(val, self.ldgr.value("firms"))
        self.assertEqual(val, self.ldgr.value("loans"))

    def test_annual_bank_charge(self):
        loan = 100
        self.ldgr.commit(loan, columns["loans"])
        annual = bank_charge(self.ldgr, YEAR)
        self.assertEqual(5, annual)
        self.assertEqual(-5, self.ldgr.value("licence"))
        self.assertEqual(loan + 5, self.ldgr.value("loans"))
        self.assertEqual(-5, self.ldgr.value("vault"))
        self.assertEqual(5, self.ldgr.value("safe"))

    def test_monthly_bank_charge(self):
        loan = 100
        self.ldgr.commit(loan, columns["loans"])
        n = x = 0
        while n < 12:
            n += 1
            x += bank_charge(self.ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(5), x, places=0)
        self.assertAlmostEqual(-5, self.ldgr.value("licence"), places=0)
        self.assertAlmostEqual(loan + 5, self.ldgr.value("loans"), places=0)
        self.assertAlmostEqual(-5, self.ldgr.value("vault"), places=0)
        self.assertAlmostEqual(5, self.ldgr.value("safe"), places=0)

    def test_annual_nonbank_interest(self):
        loan = 100
        self.ldgr.commit(loan, columns["firms"])
        annual = nonbank_interest(self.ldgr, YEAR)
        self.assertEqual(2, annual)
        self.assertAlmostEqual(-2, self.ldgr.value("safe"))
        self.assertAlmostEqual(102, self.ldgr.value("firms"))

    def test_monthly_nonbank_interest(self):
        loan = 100
        self.ldgr.commit(loan, columns["firms"])
        n = x = 0
        while n < 12:
            n += 1
            x += nonbank_interest(self.ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(2), x, places=1)
        self.assertAlmostEqual(-2, self.ldgr.value("safe"), places=1)
        self.assertAlmostEqual(102, self.ldgr.value("firms"), places=1)

    def test_firms_wages(self):
        bal = int(1E5)
        self.ldgr.commit(bal, columns["firms"])
        val = firms_wages(self.ldgr, YEAR)
        self.assertEqual(bal-val, self.ldgr.value("firms"))
        self.assertEqual(val, self.ldgr.value("workers"))

    def test_nonfirms_consumption(self):
        safe = int(26E9)
        workers = int(1E3)
        self.ldgr.commit(safe, columns["safe"])
        self.ldgr.commit(workers, columns["workers"])
        val = nonfirms_consumption(self.ldgr, YEAR / 26)
        self.assertAlmostEqual(
            Decimal(1E9 + 1E3),
            self.ldgr.value("firms"), places=6)

    def test_annual_firms_repayment(self):
        bal = int(1E7)
        self.ldgr.commit(bal, columns["loans"])
        val = firms_repayment(self.ldgr, YEAR, interest=0)
        self.assertEqual(Decimal(1E6), val)
        self.assertEqual(bal-val, self.ldgr.value("loans"))
        self.assertEqual(-val, self.ldgr.value("firms"))
        self.assertEqual(val, self.ldgr.value("vault"))

    def test_annual_firms_repayment_with_interest(self):
        bal = int(1E7)
        self.ldgr.commit(bal, columns["loans"])
        val = firms_repayment(self.ldgr, YEAR, interest=Decimal(5E5))
        self.assertEqual(Decimal(1.5E6), val)
        self.assertEqual(bal-val, self.ldgr.value("loans"))
        self.assertEqual(-val, self.ldgr.value("firms"))
        self.assertEqual(val, self.ldgr.value("vault"))


class SimulationTests(functest.TestCase):
    """
    Attempt to recreate the simulation described by Steve Keen in
    'Debunking Economics' 2nd Ed 2011. Page 363, Para 107.

    * Vault starts with $100 million
    * Simulation runs for 10 years

    Steady state:

    ======= =========
    Account $ million
    ======= =========
    Vault   16.9
    Owing   83.1
    Safe     2.7
    Firms   72.1
    Workers  8.3
    ======= =========
    """

    def test_rounding(self):
        # A reminder of how Decimal rounding works
        self.assertEqual(
            Decimal("16.9E6"),
            Decimal('16873357.20273378125176183675').quantize(
                Decimal("0.1E6"), rounding=ROUND_UP)
            )

    def test_final_values(self):
        print("\nMoney simulation in progress...")
        ledger = Ledger(*columns.values(), ref=Cy.USD)
        sim = simulate(samples=[10 * YEAR], ledger=ledger)
        output = ""
        try:
            while True:
                output += next(sim)
        except StopIteration as end:
            ldgr = end.value
            self.assertIs(ledger, ldgr)
            print(output)
            self.assertEqual(
                Decimal("16.9E6"),
                ldgr.value("vault").quantize(Decimal("0.1E6")))
            self.assertEqual(
                Decimal("83.1E6"),
                ldgr.value("loans").quantize(Decimal("0.1E6")))
            self.assertEqual(
                Decimal("2.7E6"),
                ldgr.value("safe").quantize(Decimal("0.1E6")))
            self.assertEqual(
                Decimal("72.1E6"),
                ldgr.value("firms").quantize(Decimal("0.1E6")))
            self.assertEqual(
                Decimal("8.3E6"),
                ldgr.value("workers").quantize(Decimal("0.1E6")))
