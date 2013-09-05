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


TradeFees = namedtuple("TradeFees", ["rcv", "out"])

TradePath = namedtuple("TradePath", ["rcv", "work", "out"])
TradePath.__doc__ = """`{}`

A 3-tuple of Currency_ objects, describing the path of a foreign
exchange trade. The first element is the source currency, the second the
reference currency of the account, and the third the destination currency.
""".format(TradePath.__doc__)

TradeGain = namedtuple("TradeGain", ["rcv", "gain", "out"])
TradeGain.__doc__ = """`{}`

A 3-tuple of numerical values, describing the result of a change in foreign
exchange rates. The first element is the value due to the prior rate, the
second is the gain due to the rate change, and the third element is the final
sum. """.format(TradeGain.__doc__)
