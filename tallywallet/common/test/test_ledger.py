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

import datetime
from decimal import Decimal as Dl
import unittest

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.exchange import Exchange
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
from tallywallet.common.ledger import Status
from tallywallet.common.trade import TradePath


class LedgerTests(unittest.TestCase):

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
            Column("Canadian cash", Cy.CAD, Role.asset, "{}"),
            Column("US cash", Cy.USD, Role.asset, "{}"),
            Column("Capital", Cy.CAD, Role.capital, "{}"),
            ref=Cy.CAD)
        usC = ldgr.columns["US cash"]
        for args in ldgr.adjustments(
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

        trade, col, exchange = next(ldgr.adjustments(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.3")}),
            [usC]))
        self.assertIs(col, usC)
        self.assertEqual(10, trade.gain)

        trade, col, exchange = next(ldgr.adjustments(
            Exchange({(Cy.USD, Cy.CAD): Dl("1.25")}),
            [usC]))
        self.assertIs(col, usC)
        self.assertEqual(5, trade.gain)

        trade, col, exchange = next(ldgr.adjustments(
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
            Column("Canadian cash", Cy.CAD, Role.asset, "{}"),
            Column("US cash", Cy.USD, Role.asset, "{}"),
            Column("Capital", Cy.CAD, Role.capital, "{}"),
            Column("Expense", Cy.CAD, Role.expense, "{}"),
            ref=Cy.CAD)

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
        for args in ldgr.adjustments(exchange):
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
        for args in ldgr.adjustments(exchange):
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
        for args in ldgr.adjustments(exchange):
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
