#!/usr/bin/env python3.4
#   encoding: UTF-8

from collections import deque
from collections import namedtuple
from collections import OrderedDict
import datetime
import decimal
from decimal import Decimal as Dl
import enum
import functools
import unittest
import warnings

@enum.unique
class Status(enum.Enum):
    ok = "OK"
    blocked = "BLOCKED"
    failed = "FAILED"
    stopped = "STOPPED"
    error = "ERROR"
    timedout = "TIMED OUT"


@enum.unique
class Currency(enum.Enum):
    bitcoin = "XBC"
    canadian = "CAD"
    dollar = "USD"
    pound = "GBP"
    tallywallet = "XTW"
Cy = Currency

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

TradeFees = namedtuple("TradeFees", ["rcv", "out"])
TradePath = namedtuple("TradePath", ["rcv", "work", "out"])
TradeGain = namedtuple("TradeGain", ["rcv", "gain", "out"])

class Ledger(object):

    def __init__(self, *args):
        self._cols = list(args)
        self._cols.extend(
            Column("{} trading account".format(c.value), c, Role.trading)
            for c in set(i.currency for i in args))
        self._tally = OrderedDict((i, decimal.Decimal(0)) for i in args)
        self._transactions = []
        self._rates = deque([], maxlen=2)

    def __enter__(self, *args):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def __iter__(self):
        return iter(self._transactions)

    def set_exchange(self, src, dst, fn, **kwargs):
        preFn = self._exchange.get((src, dst), lambda x: decimal.Decimal(0))
        self._exchange[(src, dst)] = fn
        assetCols = (i for i in self._cols if i.currency is src and
            i.role is Role.asset)
        tradeCol = next(i for i in self._cols
            if i.currency is src and i.role is Role.trading)
        preVals = [preFn(self._tally[i]) for i in assetCols]
        return (self._exchange, kwargs, Status.ok)
    
    def set_exchange(self, exchange, **kwargs):
        self._rates.appendleft(exchange)
        return (self._rates[0], kwargs, Status.ok)

    def add_entry(self, *args, **kwargs):
        for k, v in zip(self._cols, args):
            self._tally[k] += v
        return (args, kwargs, Status.ok)


def convert(self, val, path, fees=TradeFees(0, 0)):
    work = (val - fees.rcv) * self[(path.rcv, path.work)]
    rv = work * self[(path.work, path.out)] - fees.out
    return rv

def trade(self, val, path, prior=None, fees=TradeFees(0, 0)):
    prior = prior or self
    this = self.convert(val, path, fees)
    that = prior.convert(val, path, fees)
    return TradeGain(val, this - that, this)

Exchange = type("Exchange", (dict,), {"convert": convert, "trade": trade})

class ExchangeTests(unittest.TestCase):

    def test_conversion(self):
        exchng = Exchange({
            (Cy.pound, Cy.pound): 1,
            (Cy.pound, Cy.dollar): 2
        })
        self.assertEqual(3.0,
            exchng.convert(1.5, path=TradePath(Cy.pound, Cy.pound, Cy.dollar)))
        
    def test_null_currency_trade(self):
        exchange = Exchange({
            (Cy.pound, Cy.pound): Dl(1)
        })
        trader = functools.partial(
            exchange.trade, path=TradePath(Cy.pound, Cy.pound, Cy.pound))

        rv = trader(Dl(0))
        self.assertIsInstance(rv, TradeGain)

        self.assertEqual(trader(Dl(1)), (Dl(1), Dl(0), Dl(1)))
         
    def test_reference_currency_trade(self):
        then = Exchange({
            (Currency.pound, Currency.pound): 1,
            (Currency.pound, Currency.dollar): Dl("1.55")
        })
        
        now = Exchange({
            (Currency.pound, Currency.pound): 1,
            (Currency.pound, Currency.dollar): Dl("1.90")
        })
        
        trade = now.trade(
            10, path=TradePath(Cy.pound, Cy.pound, Cy.dollar), prior=then)
        self.assertEqual(10, trade.rcv)
        self.assertEqual(3.5, trade.gain)
        self.assertEqual(19, trade.out)

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
        with decimal.localcontext() as computation, Ledger(
            Column("Canadian cash", Cy.canadian, Role.asset),
            Column("US cash", Cy.dollar, Role.asset),
            Column("Capital", Cy.canadian, Role.capital),
        ) as ldgr:
            computation.prec = 10
            print(ldgr._cols)
            txn = ldgr.set_exchange(
                Exchange({
                    (Cy.canadian, Cy.canadian): 1,
                    (Cy.canadian, Cy.dollar): Dl("1.2")
                }),
                ts=datetime.date(2013, 1, 1), note="1 USD = 1.20 CAD")
            txn = ldgr.add_entry(
                Dl(60), Dl(100), Dl(180),
                ts=datetime.date(2013, 1, 1), note="Initial balance")
            txn = ldgr.set_exchange(
                Exchange({
                    (Cy.canadian, Cy.canadian): 1,
                    (Cy.canadian, Cy.dollar): Dl("1.3")
                }),
                ts=datetime.date(2013, 1, 2), note="1 USD = 1.30 CAD")
            txn = ldgr.set_exchange(
                Exchange({
                    (Cy.canadian, Cy.canadian): 1,
                    (Cy.canadian, Cy.dollar): Dl("1.25")
                }),
                ts=datetime.date(2013, 1, 3), note="1 USD = 1.25 CAD")
            txn = ldgr.set_exchange(
                Exchange({
                    (Cy.canadian, Cy.canadian): 1,
                    (Cy.canadian, Cy.dollar): Dl("1.25")
                }),
                ts=datetime.date(2013, 1, 4), note="1 USD = 1.15 CAD")

if __name__ == "__main__":
    unittest.main()
