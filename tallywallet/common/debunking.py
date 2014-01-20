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
import warnings

from tallywallet.common.currency import Currency as Cy
from tallywallet.common.ledger import Column
from tallywallet.common.ledger import Ledger
from tallywallet.common.ledger import Role
from tallywallet.common.ledger import Status
from tallywallet.common.output import metadata
from tallywallet.common.output import transaction

__doc__ = """
TODO:

5. Record Interest
9. Pay Worker Deposit Interest
"""

__all__ = [
    "HOUR", "DAY", "WEEK", "YEAR",
    "INITIAL",
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
        Column("licence", Cy.USD, Role.asset),
        Column("loans", Cy.USD, Role.asset),
        Column("vault", Cy.USD, Role.liability),
        Column("firms", Cy.USD, Role.liability),
        Column("workers", Cy.USD, Role.liability),
        Column("safe", Cy.USD, Role.income),
        ))


def bank_loan(ldgr, dt, pa=Decimal("0.5")):
    """
    2. Lend money
    3. Record loan
    """
    rv = ldgr.value("vault") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["licence"])
    ldgr.commit(rv, columns["loans"])
    ldgr.commit(-rv, columns["vault"])
    ldgr.commit(rv, columns["firms"])
    return rv


def bank_charge(ldgr, dt, pa=Decimal("5E-2")):
    """
    This makes sense because a Bank wants to reduce its liabilities
    at every opportunity. Interest is charged immediately as revenue
    which reduces the level in the vault. Interest is issued as a
    loan so the ledger goes up and the value is deducted from the licence.
    4. Charge interest
    5. Record interest
    """
    rv = ldgr.value("loans") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["licence"])
    ldgr.commit(rv, columns["loans"])
    ldgr.commit(-rv, columns["vault"])
    ldgr.commit(rv, columns["safe"])
    return rv


def firms_repay(ldgr, dt, interest, pa=Decimal("0.1")):
    """
    6. Repay Loan and Interest
    7. Record Loan and Interest Repayment
    """
    principal = ldgr.value("loans") * pa * Decimal(dt / YEAR)
    ldgr.commit(principal, columns["licence"])
    ldgr.commit(-principal, columns["loans"])
    ldgr.commit(principal, columns["vault"])
    ldgr.commit(-principal, columns["firms"])
    ldgr.commit(interest, columns["licence"])
    ldgr.commit(-interest, columns["loans"])
    ldgr.commit(interest, columns["vault"])
    ldgr.commit(-interest, columns["firms"])
    return principal


def firms_interest(ldgr, dt, pa=Decimal("2E-2")):
    """
    8. Pay firm deposit interest
    9. TODO: Pay worker deposit interest
    """
    rv = ldgr.value("firms") * pa * Decimal(dt / YEAR)
    ldgr.commit(rv, columns["firms"])
    ldgr.commit(-rv, columns["safe"])
    return rv


def firms_wages(ldgr, dt, pa=Decimal(3)):
    """
    10. Hire Workers
    """
    rv = ldgr.value("firms") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["firms"])
    ldgr.commit(rv, columns["workers"])
    return rv


def nonfirms_consume(ldgr, dt, paB=Decimal(1), paW=Decimal(26)):
    """
    11. Workers' Consumption
    12. Bankers' Consumption
    """
    banks = ldgr.value("safe") * paB * Decimal(dt / YEAR)
    workers = ldgr.value("workers") * paW * Decimal(dt / YEAR)
    ldgr.commit((banks + workers), columns["firms"])
    ldgr.commit(-workers, columns["workers"])
    ldgr.commit(-banks, columns["safe"])
    return banks + workers


def simulate(samples, initial=INITIAL, interval=HOUR, ledger=None):
    t = 0
    ldgr = ledger or Ledger(*columns.values(), ref=Cy.USD)
    cols = ldgr.columns
    yield metadata(ldgr)

    ldgr.commit(initial, cols["licence"])
    ldgr.commit(initial, cols["vault"])

    yield transaction(
        ldgr, ts=t, note="Keen Money Circuit with balanced accounting")

    while samples:
        t += interval
        bank_loan(ldgr, interval),
        interest = bank_charge(ldgr, interval)
        flows = (
            firms_repay(ldgr, interval, interest),
            firms_interest(ldgr, interval),
            firms_wages(ldgr, interval),
            nonfirms_consume(ldgr, interval))

        if not ldgr.equation.status is Status.ok:
            warnings.warn(
                "# Unbalanced ledger\n{}".format(transaction(ldgr)))

        if t >= samples[0]:
            yield transaction(ldgr, ts=t)
            samples.pop(0)
    return ldgr


def main(args):
    warnings.simplefilter("error")
    samples = [YEAR * i for i in range(11)]
    for msg in simulate(samples, args.initial, args.interval):
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
