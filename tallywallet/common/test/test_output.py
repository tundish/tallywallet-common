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
import io
import unittest

import rson

import tallywallet.common
from tallywallet.common.currency import Currency as Cy
from tallywallet.common.exchange import Exchange
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
from tallywallet.common.ledger import Status
from tallywallet.common.output import metadata
from tallywallet.common.output import journal


class OutputTests(unittest.TestCase):

    def test_output_metadata(self):
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset, "{}"),
            Column("US cash", Cy.USD, Role.asset, "{}"),
            Column("Capital", Cy.CAD, Role.capital, "{}"),
            Column("Expense", Cy.CAD, Role.expense, "{}"),
            ref=Cy.CAD)

        m = metadata(ldgr)
        out = rson.loads(m)
        self.assertEqual(2, len(out))
        self.assertIn("header", out[0])
        self.assertEqual(
            tallywallet.common.__version__,
            str(out[0]["header"]["version"])
        )

        self.assertIn("ledger", out[1])
        # Two columns are added by ledger for USD and CAD trading
        self.assertEqual(6, len(out[1]["ledger"]["columns"]))
        self.assertEqual("CAD", out[1]["ledger"]["ref"])

    def test_output_journal(self):
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset, "{}"),
            Column("US cash", Cy.USD, Role.asset, "{}"),
            Column("Capital", Cy.CAD, Role.capital, "{}"),
            Column("Expense", Cy.CAD, Role.expense, "{}"),
            ref=Cy.CAD)

        for amount, col in zip(
            (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
        ):
            (_, _, _, _, st) = ldgr.commit(amount, col)

        self.assertIs(Status.ok, st)
        t = journal(
            ldgr,
            ts=datetime.date(2013, 1, 1), note="Opening balance")
        out = rson.loads(t)
        self.assertEqual(2, len(out))
        self.assertEqual(
            {"ts": "2013-01-01", "note": "Opening balance"},
            out[0])
        self.assertEqual(6, len(out[1]))
        self.assertEqual(400, sum(out[1]))

    def test_output_sequential_journals(self):
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset, "{}"),
            Column("US cash", Cy.USD, Role.asset, "{}"),
            Column("Capital", Cy.CAD, Role.capital, "{}"),
            Column("Expense", Cy.CAD, Role.expense, "{}"),
            ref=Cy.CAD)
        cols = ldgr.columns

        for amount, col in zip(
            (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
        ):
            ldgr.commit(amount, col)

        out = io.StringIO()
        print(metadata(ldgr), file=out)
        print(journal(
            ldgr,
            ts=datetime.date(2013, 1, 1), note="Opening balance"),
            file=out)

        exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.2")})
        for args in ldgr.adjustments(exchange):
            ldgr.commit(*args)

        print(journal(
            ldgr,
            ts=datetime.date(2013, 1, 2), note="1 USD -> 1.20 CAD"),
            file=out)

        ldgr.commit(-20, cols["Canadian cash"])
        ldgr.commit(20, cols["Expense"])

        print(journal(
            ldgr,
            ts=datetime.date(2013, 1, 3), note="Buy food"),
            file=out)

        objs = rson.loads(out.getvalue())
        self.assertEqual(8, len(objs))
        self.assertEqual([180., 0., 200., 20., 0., 0.], objs[-1])
