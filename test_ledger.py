#!/usr/bin/env python3.4
#   encoding: UTF-8

from collections import defaultdict
from collections import namedtuple
import datetime
import decimal
import enum
import unittest
import warnings

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

Column = namedtuple("LedgerColumn", ["name", "currency", "role"])

class Ledger(object):

    def __init__(self, *args):
        self._cols = args
        self._tally = defaultdict(decimal.Decimal)
        self._transactions = []
        self._rates = {}

    def __enter__(self, *args):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def __iter__(self):
        return iter(self._transactions)

    def exchange(self, src, dst, val, **kwargs):
        self._rates[(src, dst)] = val

    def trade(self, src, dst, val=None, **kwargs):
        src = next(i for i in self._cols if i.name == src)
        dst = next(i for i in self._cols if i.name == dst)
        val = val if val is not None else 0
        rate = self._rates[(src.currency, dst.currency)]
        try:
            tallyCol = next(i for i in self._cols
                if i.currency is src.currency and i.role is Role.trading)
        except StopIteration:
            warnings.warn(
                "Ledger lacks a trading column for {}".format(
                    src.currency.name.capitalize()))
        else:
            self._tally[tallyCol] += val * rate


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
        with decimal.localcontext() as computation, Ledger(
            Column("Canadian cash", Cy.canadian, Role.asset),
            Column("US cash", Cy.dollar, Role.asset),
            Column("Capital", Cy.canadian, Role.capital),
            Column("Gain", Cy.dollar, Role.trading)
        ) as ldgr:
            computation.prec = 10
            ldgr.exchange(
                Cy.dollar, Cy.canadian, Dl(1.2),
                ts=datetime.date(2013, 1, 1))
            ldgr.trade(
                "US cash", "Canadian cash",
                ts=datetime.date(2013, 1, 1))
        print(ldgr._tally)
        print(list(ldgr))
        self.assertEqual(-5, list(ldgr)[-1][-1])

if __name__ == "__main__":
    unittest.main()
