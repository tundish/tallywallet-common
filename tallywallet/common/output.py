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

import tallywallet.common



template = """
# Metadata
{{}}
    header:version: {version}
{{}}
    ledger:columns:    [
            [Canadian cash, CAD, asset],
            [US cash, USD, asset],
            [Capital, CAD, capital],
            [Expense, CAD, asset]
        ]
    ledger:ref: {}
"""
"""
# Time series
{{}}
    note:
        initial balance
    ts:
        2013-01-01
[1,2,3]
"""

def metadata(ledger):
    columns = ",\n".join(
        " "*12 + "[{0.name}, {0.currency.name}, {0.role.name}]".format(i)
        for i in ledger._cols)
    template = """
# Metadata
{{}}
    header:version: {version}
{{}}
    ledger:columns:    [
{cols}
        ]
    ledger:ref: {}
"""
    return template.format("pooo",
        cols=columns, version=tallywallet.common.__version__)
