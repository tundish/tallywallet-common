#!/usr/bin/env python3
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

import argparse
from collections import Counter
from collections import OrderedDict
from decimal import Decimal
import sys

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
from tallywallet.common.ledger import Status
from tallywallet.common.output import metadata
from tallywallet.common.output import transaction

__doc__ = """
"""

__all__ = [
    "HOUR", "DAY", "WEEK", "YEAR",
    "bank_loan", "bank_charge",
    "firms_interest", "firms_repay", "firms_wages", "nonfirms_consume",
    "columns", "simulate"
]

SEC = 1
HOUR = 60 * 60 * SEC
DAY = 24 * HOUR
WEEK = 7 * DAY
YEAR = 52 * WEEK

INITIAL = int(100E6)

columns = OrderedDict(
    (i.name, i) for i in (
        Column("vault", Cy.USD, Role.asset),
        Column("safe", Cy.USD, Role.asset),
        Column("owing", Cy.USD, Role.capital),
        Column("firms", Cy.USD, Role.expense),
        Column("workers", Cy.USD, Role.expense)))


def bank_loan(ldgr, dt, pa=Decimal("0.5")):
    rv = ldgr.value("vault") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["vault"])
    ldgr.commit(rv, columns["firms"])
    ldgr.commit(rv, columns["owing"])
    return rv


def bank_charge(ldgr, dt, pa=Decimal("5E-2")):
    rv = ldgr.value("owing") * pa * Decimal(dt / YEAR)
    ldgr.commit(rv, columns["safe"])
    ldgr.commit(-rv, columns["firms"])
    return rv


def firms_interest(ldgr, dt, pa=Decimal("2E-2")):
    rv = ldgr.value("firms") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["safe"])
    ldgr.commit(rv, columns["firms"])
    return rv


def firms_wages(ldgr, dt, pa=Decimal(3)):
    rv = ldgr.value("firms") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["firms"])
    ldgr.commit(rv, columns["workers"])
    return rv


def nonfirms_consume(ldgr, dt, paB=Decimal(1), paW=Decimal(26)):
    banks = ldgr.value("safe") * paB * Decimal(dt / YEAR)
    workers = ldgr.value("workers") * paW * Decimal(dt / YEAR)
    ldgr.commit(-banks, columns["safe"])
    ldgr.commit(-workers, columns["workers"])
    ldgr.commit((banks + workers), columns["firms"])
    return banks + workers


def firms_repay(ldgr, dt, pa=Decimal("0.1")):
    rv = ldgr.value("owing") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["firms"])
    ldgr.commit(rv, columns["vault"])
    ldgr.commit(-rv, columns["owing"])
    return rv


def simulate(interval, samples, ledger=None):
    t = 0
    ldgr = ledger or Ledger(*columns.values(), ref=Cy.USD)
    cols = ldgr.columns
    yield metadata(ldgr)

    ldgr.commit(INITIAL, cols["vault"])
    yield transaction(
        ldgr, ts=t, note="Keen Money Circuit with balanced accounting")

    while samples:
        t += interval
        flows = (
            bank_loan(ldgr, interval),
            bank_charge(ldgr, interval),
            firms_interest(ldgr, interval),
            firms_wages(ldgr, interval),
            nonfirms_consume(ldgr, interval),
            firms_repay(ldgr, interval))

        if t >= samples[0]:
            yield transaction(ldgr, ts=t)
            samples.pop(0)
    return ldgr


def main(args):
    samples = [YEAR * i for i in range(11)]
    for msg in simulate(args.interval, samples):
        print(msg)
    return len(samples) and 1  # an error if samples not empty


def parser():
    rv = argparse.ArgumentParser(description=__doc__)
    rv.add_argument(
        "--initial", type=int, default=INITIAL,
        help="Set the initial level of vault funds [{}]".format(INITIAL))
    rv.add_argument(
        "--interval", type=int, default=HOUR,
        help="Set the simulation interval (s) [{}]".format(HOUR))
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
