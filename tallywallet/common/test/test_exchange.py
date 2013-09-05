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

from decimal import Decimal as Dl
import functools
import unittest

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.exchange import Exchange
from tallywallet.common.trade import TradeGain
from tallywallet.common.trade import TradePath


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
            exchange.gain, path=TradePath(Cy.GBP, Cy.GBP, Cy.GBP))

        rv = trader(Dl(0))
        self.assertIsInstance(rv, TradeGain)

        self.assertEqual(trader(Dl(1)), (Dl(1), Dl(0), Dl(1)))

    def test_reference_currency_trade(self):
        then = Exchange({
            (Cy.GBP, Cy.GBP): 1,
            (Cy.GBP, Cy.USD): Dl("1.55")
        })

        now = Exchange({
            (Cy.GBP, Cy.GBP): 1,
            (Cy.GBP, Cy.USD): Dl("1.90")
        })

        trade = now.gain(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD), prior=then)
        self.assertEqual(10, trade.rcv)
        self.assertEqual(3.5, trade.gain)
        self.assertEqual(19, trade.out)

    def test_unity_rate_inferred(self):
        asym = Exchange({
            (Cy.GBP, Cy.USD): Dl(2),
            (Cy.USD, Cy.GBP): Dl(0.5)
        })

        val = asym.convert(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD))
        self.assertEqual(20, val)

        val = asym.convert(
            20, path=TradePath(Cy.USD, Cy.GBP, Cy.GBP))
        self.assertEqual(10, val)

    def test_rate_inferred_from_inverse(self):
        asym = Exchange({
            (Cy.GBP, Cy.GBP): Dl(1),
            (Cy.USD, Cy.USD): Dl(1),
            (Cy.GBP, Cy.USD): Dl(2)
        })

        val = asym.convert(
            10, path=TradePath(Cy.GBP, Cy.GBP, Cy.USD))
        self.assertEqual(20, val)

        val = asym.convert(
            20, path=TradePath(Cy.USD, Cy.GBP, Cy.GBP))
        self.assertEqual(10, val)


if __name__ == "__main__":
    unittest.main()
