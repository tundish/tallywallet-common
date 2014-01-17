#!/usr/bin/env python3
#   encoding: UTF-8

from collections import Counter
from decimal import Decimal
import unittest


from tallywallet.common.debunking import *
 
class DebunkingTests(unittest.TestCase):

    def test_loan(self):
        cap = int(1E6)
        ldgr = Counter(vault=cap)
        val = bank_loan(ldgr, YEAR)
        self.assertEqual(cap-val, ldgr["vault"])
        self.assertEqual(val, ldgr["firms"])
        self.assertEqual(val, ldgr["owing"])

    def test_annual_bank_charge(self):
        loan = 100
        ldgr = Counter(owing=loan)
        annual = bank_charge(ldgr, YEAR)
        self.assertEqual(5, annual)
        self.assertEqual(-5, ldgr["firms"])
        self.assertEqual(5, ldgr["safe"])

    def test_monthly_bank_charge(self):
        loan = 100
        ldgr = Counter(owing=loan)
        n = x = 0
        while n < 12:
            n += 1
            x += bank_charge(ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(5), x, places=9)
        self.assertAlmostEqual(-5, ldgr["firms"])
        self.assertAlmostEqual(5, ldgr["safe"])

    def test_annual_firms_interest(self):
        loan = 100
        ldgr = Counter(firms=loan)
        annual = firms_interest(ldgr, YEAR)
        self.assertEqual(2, annual)
        self.assertAlmostEqual(-2, ldgr["safe"])
        self.assertAlmostEqual(102, ldgr["firms"])

    def test_monthly_firms_interest(self):
        loan = 100
        ldgr = Counter(firms=loan)
        n = x = 0
        while n < 12:
            n += 1
            x += firms_interest(ldgr, YEAR / 12)
        self.assertAlmostEqual(Decimal(2), x, places=1)
        self.assertAlmostEqual(-2, ldgr["safe"], places=1)
        self.assertAlmostEqual(102, ldgr["firms"], places=1)

    def test_firms_wages(self):
        bal = int(1E5)
        ldgr = Counter(firms=bal)
        val = firms_wages(ldgr, YEAR)
        self.assertEqual(bal-val, ldgr["firms"])
        self.assertEqual(val, ldgr["workers"])

    def test_nonfirms_consumption(self):
        safe = int(26E9)
        workers = int(1E3)
        ldgr = Counter(safe=safe, workers=workers)
        val = nonfirms_consume(ldgr, YEAR / 26)
        self.assertAlmostEqual(Decimal(1E9 + 1E3), ldgr["firms"], places=6)

    def test_annual_firms_repay(self):
        bal = int(1E7)
        ldgr = Counter(owing=bal)
        val = firms_repay(ldgr, YEAR)
        self.assertEqual(Decimal(1E6), val)
        self.assertEqual(bal-val, ldgr["owing"])
        self.assertEqual(-val, ldgr["firms"])
        self.assertEqual(val, ldgr["vault"])
