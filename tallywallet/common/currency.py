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

import enum

__doc__ = """
The currency module defines currencies of various types. As of this
release, there are only a handful yet defined.
"""


@enum.unique
class Currency(enum.Enum):
    """
    This is an enumeration class which captures the codes defined in
    `ISO 4217`_ for international currencies.

    .. _ISO 4217: http://en.wikipedia.org/wiki/ISO_4217
    """
    CAD = 124
    USD = 840
    GBP = 826
    XBC = "bitcoin"
    XTW = "tallywallet"
