#!/usr/bin/env python3
#   encoding: UTF-8

from decimal import Decimal
from decimal import ROUND_UP
import unittest

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.debunking import *
from tallywallet.common.exchange import Exchange
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
 

class DebunkingTests(unittest.TestCase):

    def setUp(self):
        self.ldgr = Ledger(
            Column("vault", Cy.USD, Role.asset),
            Column("safe", Cy.USD, Role.asset),
            Column("owing", Cy.USD, Role.capital),
            Column("firms", Cy.USD, Role.expense),
            Column("workers", Cy.USD, Role.expense),
            ref=Cy.USD)

    def test_loan(self):
        cap = int(1E6)
        val = bank_loan(ldgr, YEAR)
        self.assertEqual(cap-val, self.ldgr["vault"])
        self.assertEqual(val, self.ldgr["firms"])
        self.assertEqual(val, self.ldgr["owing"])

    def test_annual_bank_charge(self):
        loan = 100
        annual = bank_charge(self.ldgr, YEAR)
        self.assertEqual(5, annual)
        self.assertEqual(-5, self.ldgr["firms"])
        self.assertEqual(5, self.ldgr["safe"])

    def test_monthly_bank_charge(self):
        loan = 100
        n = x = 0
        while n < 12:
            n += 1
            x += bank_charge(self.ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(5), x, places=9)
        self.assertAlmostEqual(-5, self.ldgr["firms"])
        self.assertAlmostEqual(5, self.ldgr["safe"])

    def test_annual_firms_interest(self):
        loan = 100
        annual = firms_interest(self.ldgr, YEAR)
        self.assertEqual(2, annual)
        self.assertAlmostEqual(-2, self.ldgr["safe"])
        self.assertAlmostEqual(102, self.ldgr["firms"])

    def test_monthly_firms_interest(self):
        loan = 100
        n = x = 0
        while n < 12:
            n += 1
            x += firms_interest(self.ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(2), x, places=1)
        self.assertAlmostEqual(-2, self.ldgr["safe"], places=1)
        self.assertAlmostEqual(102, self.ldgr["firms"], places=1)

    def test_firms_wages(self):
        bal = int(1E5)
        val = firms_wages(self.ldgr, YEAR)
        self.assertEqual(bal-val, self.ldgr["firms"])
        self.assertEqual(val, self.ldgr["workers"])

    def test_nonfirms_consumption(self):
        safe = int(26E9)
        workers = int(1E3)
        val = nonfirms_consume(self.ldgr, YEAR / 26)
        self.assertAlmostEqual(Decimal(1E9 + 1E3), self.ldgr["firms"], places=6)

    def test_annual_firms_repay(self):
        bal = int(1E7)
        val = firms_repay(self.ldgr, YEAR)
        self.assertEqual(Decimal(1E6), val)
        self.assertEqual(bal-val, self.ldgr["owing"])
        self.assertEqual(-val, self.ldgr["firms"])
        self.assertEqual(val, self.ldgr["vault"])


class SimulationTests(unittest.TestCase):
    """
    Attempt to recreate the simulation discribed by Steve Keen in
    'Debunking Economics' 2nd Ed 2011. Page 363, Para 107.

    Vault starts with $100 million
    Simulation runs for 10 years

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
            Decimal("0.1E6"), rounding=ROUND_UP))

    def test_final_values(self):
        print("\nMoney simulation in progress...")
        output = "\n".join(simulate(HOUR, samples=[10 * YEAR]))
        print(output)
        self.assertEqual(
            Decimal("16.9E6"),
            self.ldgr["vault"].quantize(Decimal("0.1E6")))
        self.assertEqual(
            Decimal("83.1E6"),
            self.ldgr["owing"].quantize(Decimal("0.1E6")))
        self.assertEqual(
            Decimal("2.7E6"),
            self.ldgr["safe"].quantize(Decimal("0.1E6")))
        self.assertEqual(
            Decimal("72.1E6"),
            self.ldgr["firms"].quantize(Decimal("0.1E6")))
        self.assertEqual(
            Decimal("8.3E6"), self.ldgr["workers"].quantize(
            Decimal("0.1E6")))
