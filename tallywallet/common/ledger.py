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

from collections import namedtuple
from collections import OrderedDict
from decimal import Decimal as Dl
import enum
from functools import singledispatch
from numbers import Number
import warnings

from tallywallet.common.currency import Currency
from tallywallet.common.exchange import Exchange
from tallywallet.common.trade import TradePath

__doc__ = """
The ledger module defines Ledger and some associated classes.
"""


@enum.unique
class Status(enum.Enum):
    ok = "OK"
    blocked = "BLOCKED"
    failed = "FAILED"
    stopped = "STOPPED"
    error = "ERROR"
    timedout = "TIMED OUT"


class Role(enum.Enum):
    """
    This enumeration contains definitions for the roles played by
    a column in a Ledger.
    """
    asset = 1
    liability = 2
    capital = 3
    income = 4
    trading = 5
    expense = 6
    dividend = 7


Column = namedtuple("Column", ["ref", "currency", "role", "label"])
Column.__doc__ = """`{}`

A 4-tuple, describing a column in a Ledger.
""".format(Column.__doc__)

FAE = namedtuple("FundamentalAccountingEquation", ["lhs", "rhs", "status"])


def transaction(job, *args, **kwargs):
    raise NotImplementedError


class Ledger(object):
    """
    This class implements the fundamental operations you need to perform
    Adjusted Cost Base accounting.
    """
    def __init__(self, *args, ref=Currency.XTW):
        """
        :param ref: (optional) the base Currency_ type for the Ledger
        :param args: One or more Column objects
        """
        self.ref = ref
        cols = list(args)
        cols.extend(
            Column(c.name, c, Role.trading, "{} trading account")
            for c in set(i.currency for i in args))
        self._tradingAccounts = {
            i.currency: i for i in cols if i.role is Role.trading}
        self._rates = {i: Exchange({}) for i in args}
        self._tally = OrderedDict((i, Dl(0)) for i in cols)
        self.transaction = singledispatch(transaction)

    @property
    def columns(self):
        rv = OrderedDict((i.label.format(i.ref), i) for i in self._tally)
        if len(rv) != len(self._tally):
            warnings.warn("Missing key(s)")
        return rv

    @property
    def equation(self):
        """
        The `Fundamental Accounting Equation`_ is this::

            Assets - Liabilities = Capital + Income - Expenses - Dividends

        Currency trading gains are counted as income.
        For practical purposes, the `FAE` is often rearranged to be::

            Assets + Expenses + Dividends = Capital + Income + Liabilities

        This property evaluates both sides of this second equation,
        and determines if they are equal or not.

        :returns: A tuple of `lhs`, `rhs`, `status`

        .. _Fundamental Accounting Equation: \
http://en.wikipedia.org/wiki/Accounting_equation
        """
        st = Status.failed
        lhCols = set(i for i in self._tally
                     if i.role in (Role.asset, Role.expense, Role.dividend))
        trCols = set(i for i in self._tally if i.role is Role.trading)
        rhCols = set(self._tally.keys()) - lhCols - trCols
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
            if lhs.quantize(Dl("0.01")) == rhs.quantize(Dl("0.01")):
                st = Status.ok

        return FAE(lhs, rhs, st)

    def add_column(self, ref, role, *, label="{}", currency=None):
        assert role is not Role.trading
        crncy = currency or self.ref
        rv = Column(ref, crncy, role, label)
        self._tally[rv] = Dl(0)
        self._rates[rv] = Exchange({})
        if crncy not in self._tradingAccounts:
            tA = Column(crncy.name, crncy, Role.trading, "{} trading account")
            self._tradingAccounts[crncy] = tA
            self._tally[tA] = Dl(0)
        return rv

    def adjustments(self, exchange, cols=None):
        """
        Calculates the effects of a change in exchange rates.

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
        for c in cols:
            account = self._tradingAccounts[c.currency]
            trade = exchange.gain(
                self._tally[c],
                path=TradePath(c.currency, self.ref, self.ref),
                prior=self._rates.get(c))
            yield (trade, c, exchange)

    def commit(self, trade, col, exchange=None, **kwargs):
        """
        Applies a trade to the ledger.

        If you supply an exchange argument, `trade` may be a TradeGain
        object. In this usage, a trading account in the currency of the
        ledger column will accept any exchange gain or loss.

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

    def balance(self, ref):
        """
        Returns columns and their values in the ledger.

        :param ref: The ref of the column
        """
        return [(col, val) for col, val in self._tally.items()
                if col.ref == ref]

    def value(self, arg):
        """
        Returns the current value of a column in the ledger.

        :param arg: The column object, or its name as a string
        """
        try:
            return self._tally[arg]
        except KeyError:
            col = next(i for i in self._tally if i.label.format(i.ref) == arg)
            return self._tally[col]
