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

import rson

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.exchange import Exchange
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
from tallywallet.common.ledger import Status
from tallywallet.common.output import metadata
from tallywallet.common.trade import TradePath


class OutputTests(unittest.TestCase):

    def test_serialise_columns(self):
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset),
            Column("US cash", Cy.USD, Role.asset),
            Column("Capital", Cy.CAD, Role.capital),
            Column("Expense", Cy.CAD, Role.expense),
            ref=Cy.CAD)

        for amount, col in zip(
            (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
        ):
            ldgr.commit(
                amount, col,
                ts=datetime.date(2013, 1, 1), note="Opening balance")

        out = rson.loads(metadata(ldgr))
        print(out)
        self.assertEqual(2, len(out))

    def test_serialise_transactions(self):
        ldgr = Ledger(
            Column("Canadian cash", Cy.CAD, Role.asset),
            Column("US cash", Cy.USD, Role.asset),
            Column("Capital", Cy.CAD, Role.capital),
            Column("Expense", Cy.CAD, Role.expense),
            ref=Cy.CAD)

        for amount, col in zip(
            (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
        ):
            ldgr.commit(
                amount, col,
                ts=datetime.date(2013, 1, 1), note="Opening balance")

        exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.25")})
        metadata = """
# Metadata
{}
    Header:
        version: 0.002
{}
    Ledger:
        columns:    [
            (Canadian cash, CAD, asset),
            (US cash, USD, asset),
            (Capital, CAD, capital),
            (Expense, CAD, asset)
        ]
        ref: CAD
"""

        """
# Time series
[]
    [1,2]
"""
