#!/usr/bin/env python3.4
#   encoding: UTF-8

from collections import namedtuple
import datetime
import decimal
import enum
import unittest

@enum.unique
class Currency(enum.Enum):
    bitcoin = "XBC"
    canadian = "CAD"
    dollar = "USD"
    pound = "GBP"
    wellmet = "XWM"

@enum.unique
class Role(enum.Enum):
    asset = ()
    liability = ()
    capital = ()
    income = ()
    trading = ()
    expense = ()

    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

Column = namedtuple("LedgerColumn", ["name", "typ", "role"])

class Ledger(object):

    def exchange(self, src, dst, val):
        pass

    def trade(self, src, dst, val):
        pass

    def __init__(self, *args):
        self._transactions = []

    def __iter__(self):
        for i in self._transactions:
            yield i

    def load(self, entries):
        self._transactions.extend(entries)

class CurrencyTests(unittest.TestCase):

    def test_exchange_gain_with_fixed_assets(self):
        """
        From Selinger table 4.1
        date                             asset  asset   capital gain
        Jan 1 Balance (1 USD = 1.20 CAD) CAD 60 USD 100 CAD 180 CAD 0
        Jan 2 Balance (1 USD = 1.30 CAD) CAD 60 USD 100 CAD 180 CAD 10
        Jan 3 Balance (1 USD = 1.25 CAD) CAD 60 USD 100 CAD 180 CAD 5
        Jan 4 Balance (1 USD = 1.15 CAD) CAD 60 USD 100 CAD 180 – CAD 5
        """
        Cy = Currency
        Dl = decimal.Decimal
        ldgr = Ledger(
            Column("date", datetime.date, None)
        )
        ldgr.load([
            (datetime.date(2013, 1, 1),
            ldgr.exchange(Cy.dollar, Cy.canadian, Dl(1.2))),
            (datetime.date(2013, 1, 1),
            ldgr.trade(Cy.dollar, Cy.canadian, Dl(1.2)))
        ])
        self.assertEqual(-5, list(ldgr)[-1][-1])

if __name__ == "__main__":
    unittest.main()
