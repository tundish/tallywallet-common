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

__doc__ = """
The exchange module contains functionality to enable conversion between
currencies.
"""


def convert(self, val, path, fees=TradeFees(0, 0)):
    """
    Return the calculated outcome of converting the amount `val`
    via the TradePath `path`.
    """
    work = (val - fees.rcv) * self.get((path.rcv, path.work))
    rv = work * self.get((path.work, path.out)) - fees.out
    return rv


def gain(self, val, path, prior=None, fees=TradeFees(0, 0)):
    """
    Calculate the gain related to a change in exchange rates.
    The `self` object contains the latest rates, and the historic
    ones are passed as an argument to this method.

    :param prior: An Exchange_ object which contains the rates
                  existing prior to those in the `self` object.
    :rtype: TradeGain
    """
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
                {"convert": convert, "gain": gain, "get": infer_rate})
Exchange.__doc__ = """
An exchange is a lookup container for currency exchange rates.

It behaves just like a Python dictionary, but has some extra methods.

The approach Tallywallet uses is to associate each rate against a key
which is a 2-tuple of Currency_.
By convention, the first element of this key is the source currency,
and the second is the destination. The values of the exchange mapping can
therefore be considered as `gain` from one currency to the next.

.. py:method:: get(key)

   Return the value stored against `key`.

   This method overrides the standard behaviour of `dict.get`. It infers the
   values of missing keys as follows:

    * The rate of a currency against itself is unity.
    * The rate of one currency against another is the reciprocal of the
      reverse rate (if defined).
"""
