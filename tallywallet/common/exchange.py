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

from tallywallet.common.trade import TradeFees
from tallywallet.common.trade import TradeGain


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
