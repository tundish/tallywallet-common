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
from numbers import Number
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
    CAD = 124
    USD = 840
    GBP = 826
    XBC = "bitcoin"
    XTW = "tallywallet"
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

    def __init__(self, *args, ref=Currency.XTW):
        self.ref = ref
        self._cols = list(args)
        self._cols.extend(
            Column("{} trading account".format(c.name), c, Role.trading)
            for c in set(i.currency for i in args))
        self._tradingAccounts = {
            i.currency: i for i in self._cols if i.role is Role.trading}
        self._rates = {i: Exchange({}) for i in args}
        self._tally = OrderedDict((i, decimal.Decimal(0)) for i in self._cols)
        self._transactions = deque([], maxlen=200)

    def __iter__(self):
        return iter(self._transactions)

    @property
    def columns(self):
        return self._cols[:]

    def speculate(self, exchange, cols=None):
        """
        Calculates the effect of a change in exchange rates.

        Supply an Exchange object and an optional sequence of columns.
        If no columns are specified then all are assumed.

        The columns are recalculated (but not committed) against the new
        exchange rates.

        This method with generate a sequence of 3-tuples;
        `(TradeGain, Column, Exchange)`.

        This output is compatible with the arguments accepted by the `commit`
        method.
        """
        cols = cols or [i for i in self.columns if not i.role is Role.trading]
        exchange.update({(c, c): Dl(1.0) for c in self._tradingAccounts})
        for c in cols:
            account = self._tradingAccounts[c.currency]
            trade = exchange.trade(
                self._tally[c],
                path=TradePath(c.currency, self.ref, self.ref),
                prior=self._rates[c])
            yield (trade, c, exchange)

    def commit(self, trade, col, exchange=None, **kwargs):
        """
        Applies a trade to the ledger.

        If you supply an exchange rate, `trade` may be a TradeGain object.
        In this usage, a trading account in the currency of the ledger
        column will accept any exchange gain or loss.

        Otherwise, `trade` should be a number. It will be added to the
        specified column in the ledger.
        """
        exchange = exchange or self._rates[col]
        st = Status.ok
        try:
            account = self._tradingAccounts[col.currency]
            self._tally[account] += trade.gain
            self._rates[col] = exchange
        except AttributeError:
            if isinstance(trade, Number):
                self._tally[col] += trade
            else:
                st = Status.error
        return (trade, col, exchange, kwargs, st)


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
            (Cy.GBP, Cy.GBP): 1,
            (Cy.GBP, Cy.USD): 2
        })
        self.assertEqual(
            3.0,
            exchng.convert(1.5, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD)))

    def test_null_currency_trade(self):
        exchange = Exchange({
            (Cy.GBP, Cy.GBP): Dl(1)
        })
        trader = functools.partial(
            exchange.trade, path=TradePath(Cy.GBP, Cy.GBP, Cy.GBP))

        rv = trader(Dl(0))
        self.assertIsInstance(rv, TradeGain)

        self.assertEqual(trader(Dl(1)), (Dl(1), Dl(0), Dl(1)))

    def test_reference_currency_trade(self):
        then = Exchange({
            (Currency.GBP, Currency.GBP): 1,
            (Currency.GBP, Currency.USD): Dl("1.55")
        })

        now = Exchange({
            (Currency.GBP, Currency.GBP): 1,
            (Currency.GBP, Currency.USD): Dl("1.90")
        })

        trade = now.trade(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD), prior=then)
        self.assertEqual(10, trade.rcv)
        self.assertEqual(3.5, trade.gain)
        self.assertEqual(19, trade.out)


class CurrencyTests(unittest.TestCase):

    def test_track_exchange_gain_with_fixed_assets(self):
        """
        From Selinger table 4.1
        date                             asset  asset   capital gain
        Jan 1 Balance (1 USD = 1.20 CAD) CAD 60 USD 100 CAD 180 CAD 0
        Jan 2 Balance (1 USD = 1.30 CAD) CAD 60 USD 100 CAD 180 CAD 10
        Jan 3 Balance (1 USD = 1.25 CAD) CAD 60 USD 100 CAD 180 CAD 5
        Jan 4 Balance (1 USD = 1.15 CAD) CAD 60 USD 100 CAD 180 – CAD 5
        """
        with decimal.localcontext() as computation:
            computation.prec = 10
            ldgr = Ledger(
                Column("Canadian cash", Cy.CAD, Role.asset),
                Column("US cash", Cy.USD, Role.asset),
                Column("Capital", Cy.CAD, Role.capital),
                ref=Cy.CAD)
            usC = next(i for i in ldgr.columns if i.name == "US cash")
            for args in ldgr.speculate(
                Exchange({
                    (Cy.USD, Cy.CAD): Dl("1.2")
                    })):
                ldgr.commit(
                    *args, ts=datetime.date(2013, 1, 1),
                    note="1 USD = 1.20 CAD")

            for trade, col in zip(
                (Dl(60), Dl(100), Dl(180)), ldgr.columns
            ):
                ldgr.commit(
                    trade, col,
                    ts=datetime.date(2013, 1, 1), note="Initial balance")

            trade, col, exchange = next(ldgr.speculate(
                Exchange({
                    (Cy.USD, Cy.CAD): Dl("1.3")
                }),
                [usC]))
            self.assertIs(col, usC)
            self.assertEqual(10, trade.gain)

            trade, col, exchange = next(ldgr.speculate(
                Exchange({
                    (Cy.USD, Cy.CAD): Dl("1.25")
                }),
                [usC]))
            self.assertIs(col, usC)
            self.assertEqual(5, trade.gain)

            trade, col, exchange = next(ldgr.speculate(
                Exchange({
                    (Cy.USD, Cy.CAD): Dl("1.15")
                }),
                [usC]))
            self.assertIs(col, usC)
            self.assertEqual(-5, trade.gain)

if __name__ == "__main__":
    unittest.main()
