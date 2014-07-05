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

__doc__ = """
Tallywallet has chosen RSON_ as the serialisation format for a Ledger.
It's a readable serial object notation which can be processed by text
utilities or converted into Python objects.

.. _RSON: http://code.google.com/p/rson/

"""


def metadata(ledger):
    """
    Create an RSON string containing all the metadata required to recreate
    a working Ledger object.
    """
    columns = ",\n".join(
        " "*12 + "[{0}, {1.currency.name}, {1.role.name}]".format(
            i.label.format(i.ref), i)
        for i in ledger._tally)
    template = """
{{}}
    header:version: {version}
{{}}
    ledger:columns:    [
{cols}
        ]
    ledger:ref: {ref}
"""
    return template.format(
        cols=columns, ref=ledger.ref.name,
        version=tallywallet.common.__version__)


def journal(ledger, **kwargs):
    """
    Create an RSON string representing the current state of
    a Ledger object.

    Journal strings can be appended to metadata, and/or concatenated
    to form a time-series record of the Ledger accounts.
    """
    keys = sorted(kwargs.keys())
    keyargs = "\n".join(
        "{pad}{key}:\n{pad}    {val}".format(key=k, val=kwargs[k], pad=" "*4)
        for k in keys)
    data = ','.join("{: .2f}".format(i) for i in ledger._tally.values())
    return "{{}}\n{keyargs}\n[{data}]\n""".format(keyargs=keyargs, data=data)
