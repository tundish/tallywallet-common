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

FAE = namedtuple("FundamentalAccountingEquation", ["lhs", "rhs", "status"])


def convert(self, val, path, fees=TradeFees(0, 0)):
    work = (val - fees.rcv) * self.get((path.rcv, path.work))
    rv = work * self.get((path.work, path.out)) - fees.out
    return rv


def trade(self, val, path, prior=None, fees=TradeFees(0, 0)):
    prior = prior or self
    this = self.convert(val, path, fees)
    that = prior.convert(val, path, fees)
    return TradeGain(val, this - that, this)


def infer_rate(self, key):
    try:
        return self[key]
    except KeyError:
        key = tuple(reversed(key))
        try:
            return Dl(1) / self[key]
        except KeyError as err:
            if key[0] == key[1]:
                return Dl(1)
            else:
                raise err

Exchange = type("Exchange", (dict,),
                {"convert": convert, "trade": trade, "get": infer_rate})


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
        return OrderedDict((i.name, i) for i in self._cols)

    @property
    def equation(self):
        """
        Evaluates the Fundamental Accounting Equation::

            Assets - Liabilities = Capital + Income - Expenses

        hence::

            Assets + Expenses = Capital + Income + Liabilities

        Currency trading gains are counted as income.
        """
        st = Status.failed
        lhCols = set(i for i in self._cols
                     if i.role in (Role.asset, Role.expense))
        trCols = set(i for i in self._cols if i.role is Role.trading)
        rhCols = set(self._cols) - lhCols - trCols
        try:
            lhs = sum(
                self._rates[col].convert(
                    self._tally[col],
                    TradePath(col.currency, self.ref, self.ref))
                for col in lhCols)
            rhs = sum(
                self._rates[col].convert(
                    self._tally.get(col, Dl(0)),
                    TradePath(col.currency, self.ref, self.ref))
                for col in rhCols) + sum(
                self._tally.get(col, Dl(0)) for col in trCols)
        except KeyError:
            lhs = None
            rhs = None
        else:
            if lhs == rhs:
                st = Status.ok

        return FAE(lhs, rhs, st)

    def speculate(self, exchange, cols=None):
        """
        Calculates the effect of a change in exchange rates.

        Supply an Exchange object and an optional sequence of columns.
        If no columns are specified then all are assumed.

        The columns are recalculated (but not committed) against the new
        exchange rates.

        This method will generate a sequence of 3-tuples;
        `(TradeGain, Column, Exchange)`.

        This output is compatible with the arguments accepted by the `commit`
        method.
        """
        cols = cols or [i for i in self.columns.values()
                        if not i.role is Role.trading]
        exchange.update({(c, c): Dl(1.0) for c in self._tradingAccounts})
        for c in cols:
            account = self._tradingAccounts[c.currency]
            trade = exchange.trade(
                self._tally[c],
                path=TradePath(c.currency, self.ref, self.ref),
                prior=self._rates.get(c))
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
        exchange = exchange or self._rates.get(col)
        st = Status.ok
        account = self._tradingAccounts[col.currency]
        try:
            self._tally[account] += trade.gain
            self._rates[col] = exchange
        except AttributeError:
            if isinstance(trade, Number):
                self._tally[col] += trade
            else:
                st = Status.error
        return (trade, col, exchange, kwargs, st)

    def value(self, name):
        col = next(i for i in self._cols if i.name == name)
        return self._tally[col]


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

    def test_unity_rate_inferred(self):
        asym = Exchange({
            (Currency.GBP, Currency.USD): Dl(2),
            (Currency.USD, Currency.GBP): Dl(0.5)
        })

        val = asym.convert(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD))
        self.assertEqual(20, val)

        val = asym.convert(
            20, path=TradePath(Cy.USD, Cy.GBP, Cy.GBP))
        self.assertEqual(10, val)

    def test_rate_inferred_from_inverse(self):
        asym = Exchange({
            (Currency.GBP, Currency.GBP): Dl(1),
            (Currency.USD, Currency.USD): Dl(1),
            (Currency.GBP, Currency.USD): Dl(2)
        })

        val = asym.convert(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD))
        self.assertEqual(20, val)

        val = asym.convert(
            20, path=TradePath(Cy.USD, Cy.GBP, Cy.GBP))
        self.assertEqual(10, val)


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
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset),
            Column("US cash", Cy.USD, Role.asset),
            Column("Capital", Cy.CAD, Role.capital),
            ref=Cy.CAD)
        usC = ldgr.columns["US cash"]
        for args in ldgr.speculate(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.2")})
        ):
            ldgr.commit(
                *args, ts=datetime.date(2013, 1, 1),
                note="1 USD = 1.20 CAD")

        lhs, rhs, st = ldgr.equation
        self.assertEqual(lhs, rhs)
        self.assertIs(st, Status.ok)

        for deposit, col in zip(
            (Dl(60), Dl(100), Dl(180)), ldgr.columns.values()
        ):
            ldgr.commit(
                deposit, col,
                ts=datetime.date(2013, 1, 1), note="Initial balance")

        lhs, rhs, st = ldgr.equation
        self.assertEqual(lhs, rhs)
        self.assertIs(st, Status.ok)

        trade, col, exchange = next(ldgr.speculate(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.3")}),
            [usC]))
        self.assertIs(col, usC)
        self.assertEqual(10, trade.gain)

        trade, col, exchange = next(ldgr.speculate(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.25")}),
            [usC]))
        self.assertIs(col, usC)
        self.assertEqual(5, trade.gain)

        trade, col, exchange = next(ldgr.speculate(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.15")}),
            [usC]))
        self.assertIs(col, usC)
        self.assertEqual(-5, trade.gain)

        lhs, rhs, st = ldgr.equation
        self.assertEqual(lhs, rhs)
        self.assertIs(st, Status.ok)

    def test_commit_exchange_gain_via_expenses(self):
        """
        From Selinger table 4.4
        date                    asset   asset   capital expense trading
        Jan 1   Opening balance CAD 200 USD 0   CAD 200 CAD 0   USD 0 CAD 0
        Jan 2   1 USD==1.20CAD  CAD-120 USD 100                 USD 100 CAD 120
                Balance         CAD 80  USD 100 CAD 200 CAD 0   USD 100 CAD 120
        Jan 3   1 USD==1.30CAD          USD-40          CAD 52  USD-40 CAD 52
                Balance         CAD 80  USD 60  CAD 200 CAD 52  USD 60 CAD-68
        Jan 5   1 USD==1.25CAD  CAD 75  USD-60                  USD-60 CAD 75
                Balance         CAD 155 USD 0   CAD 200 CAD 52  USD 0  CAD 07
        Jan 7   Buy food        CAD-20                  CAD 20
                Balance         CAD 135 USD 0   CAD 200 CAD 72  USD 0  CAD 07
        """
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset),
            Column("US cash", Cy.USD, Role.asset),
            Column("Capital", Cy.CAD, Role.capital),
            Column("Expense", Cy.CAD, Role.expense),
            ref=Cy.CAD)

        # references to important columns
        cols = ldgr.columns

        self.assertIs(Status.failed, ldgr.equation.status)

        # row one
        for amount, col in zip(
            (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
        ):
            ldgr.commit(
                amount, col,
                ts=datetime.date(2013, 1, 1), note="Opening balance")
        self.assertEqual(200, ldgr.value("Canadian cash"))
        self.assertEqual(200, ldgr.value("Capital"))
        self.assertEqual(0, ldgr.value("USD trading account"))  # whitebox test

        self.assertIs(Status.failed, ldgr.equation.status)

        # row two
        exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.2")})
        for args in ldgr.speculate(exchange):
            ldgr.commit(
                *args, ts=datetime.date(2013, 1, 2),
                note="1 USD = 1.20 CAD")

        lhs, rhs, st = ldgr.equation
        self.assertEqual(lhs, rhs)
        self.assertIs(st, Status.ok)

        usd = exchange.convert(120, TradePath(Cy.CAD, Cy.CAD, Cy.USD))
        self.assertEqual(100, usd)
        ldgr.commit(-120, cols["Canadian cash"])
        self.assertIs(ldgr.equation.status, Status.failed)
        ldgr.commit(usd, cols["US cash"])
        self.assertIs(ldgr.equation.status, Status.ok)

        # row three
        exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.3")})
        for args in ldgr.speculate(exchange):
            ldgr.commit(
                *args, ts=datetime.date(2013, 1, 3),
                note="1 USD = 1.30 CAD")
        cad = exchange.convert(40, TradePath(Cy.USD, Cy.CAD, Cy.CAD))
        self.assertEqual(52, cad)

        self.assertIs(ldgr.equation.status, Status.ok)
        ldgr.commit(-40, cols["US cash"])
        self.assertIs(ldgr.equation.status, Status.failed)
        ldgr.commit(cad, cols["Expense"])
        self.assertIs(ldgr.equation.status, Status.ok)

        # row four
        exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.25")})
        for args in ldgr.speculate(exchange):
            ldgr.commit(
                *args, ts=datetime.date(2013, 1, 5),
                note="1 USD = 1.25 CAD")
        cad = exchange.convert(60, TradePath(Cy.USD, Cy.CAD, Cy.CAD))
        self.assertEqual(75, cad)

        self.assertIs(ldgr.equation.status, Status.ok)
        ldgr.commit(-60, cols["US cash"])
        self.assertIs(ldgr.equation.status, Status.failed)
        ldgr.commit(cad, cols["Canadian cash"])
        self.assertIs(ldgr.equation.status, Status.ok)

        self.assertEqual(155, ldgr.value("Canadian cash"))

        # row five
        ldgr.commit(-20, cols["Canadian cash"], note="Buy food")
        self.assertIs(ldgr.equation.status, Status.failed)
        ldgr.commit(20, cols["Expense"], note="Buy food")
        self.assertIs(ldgr.equation.status, Status.ok)

        # final balance
        self.assertEqual(135, ldgr.value("Canadian cash"))
        self.assertEqual(0, ldgr.value("US cash"))
        self.assertEqual(200, ldgr.value("Capital"))
        self.assertEqual(72, ldgr.value("Expense"))
        self.assertEqual(7, ldgr.value("USD trading account"))

if __name__ == "__main__":
    unittest.main()
