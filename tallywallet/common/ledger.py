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
from decimal import Decimal as Dl
import enum
from numbers import Number

from tallywallet.common.currency import Currency
from tallywallet.common.exchange import Exchange
from tallywallet.common.trade import TradePath

@enum.unique
class Status(enum.Enum):
    ok = "OK"
    blocked = "BLOCKED"
    failed = "FAILED"
    stopped = "STOPPED"
    error = "ERROR"
    timedout = "TIMED OUT"


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
FAE = namedtuple("FundamentalAccountingEquation", ["lhs", "rhs", "status"])


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
        self._tally = OrderedDict((i, Dl(0)) for i in self._cols)
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
