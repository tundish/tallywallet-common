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
from tallywallet.common.output import journal

__doc__ = """
The `tallywallet.common.debunking` module presents Keen's simulation
according to Wilson's perspective of balanced accounting.

You run it as follows::

    $ python -m tallywallet.common.debunking

Or, to make use of the advanced options, read the help like this::

    $ python -m tallywallet.common.debunking --help

"""

__all__ = [
    "HOUR", "DAY", "WEEK", "YEAR",
    "INITIAL", "banking_licence",
    "bank_loan", "bank_charge", "nonbank_interest", "firms_repayment",
    "firms_wages", "nonfirms_consumption",
    "columns", "simulate"
]

SEC = 1
HOUR = 60 * 60 * SEC
DAY = 24 * HOUR
WEEK = 7 * DAY
YEAR = 52 * WEEK

INITIAL = int(100E6)

columns = OrderedDict(
    (i.ref, i) for i in (
        Column("licence", Cy.USD, Role.asset, "{}"),
        Column("loans", Cy.USD, Role.asset, "{}"),
        Column("vault", Cy.USD, Role.liability, "{}"),
        Column("firms", Cy.USD, Role.liability, "{}"),
        Column("workers", Cy.USD, Role.liability, "{}"),
        Column("safe", Cy.USD, Role.income, "{}"),
        ))


def banking_licence(ldgr, val):
    """
    Wilson's suggestion is to formalise the ability of a bank
    to create money. His first step (not present in Keen) is
    to capture this value as an asset.

    1. Grant licence
    """
    ldgr.commit(val, columns["licence"])
    ldgr.commit(val, columns["vault"])
    return val


def bank_loan(ldgr, dt, pa=Decimal("0.5")):
    """
    These two steps create a debit against the licence and
    a corresponding addition to the loans book. The firms'
    account is credited, reducing the balance in the vault.

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
    This operation is a significant departure from Keen's original.

    In the real world, a Bank will want to reduce its liabilities
    at every opportunity. Interest is charged immediately as revenue
    which reduces the level in the vault. The interest is issued as a
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


def firms_repayment(ldgr, dt, interest, pa=Decimal("0.1")):
    """
    The interest calculated in the previous step is debited from
    the firms' account. At the same time, part of the principal
    of the loan is paid off too. The total reappears in the vault,
    reducing the loan book and accruing value back to the licence.

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
    return principal + interest


def nonbank_interest(ldgr, dt, paF=Decimal("2E-2"), paW=Decimal("3E-3")):
    """
    Keen's original model only paid interest on the firms' account.
    Wilson added interest for workers too. In order to maintain the
    equivalence of the two simulations, I have adjusted the workers'
    interest rate so that the steady state output after ten years is
    close to that described in Keen's book. This corresponds to a rate
    of 0.3% on a worker's current account which, though low, has been
    observed in the UK in recent times.

    8. Pay firm deposit interest
    9. Pay worker deposit interest
    """
    firms = ldgr.value("firms") * paF * Decimal(dt / YEAR)
    workers = ldgr.value("workers") * paW * Decimal(dt / YEAR)
    ldgr.commit(firms, columns["firms"])
    ldgr.commit(-firms, columns["safe"])
    ldgr.commit(workers, columns["workers"])
    ldgr.commit(-workers, columns["safe"])
    return firms + workers


def firms_wages(ldgr, dt, pa=Decimal(3)):
    """
    Keen models the cost of production entirely as workers'
    wages. There is no mention of capital. Clearly this is
    a simplification which we can elaborate at another opportunity.

    10. Hire Workers
    """
    rv = ldgr.value("firms") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, columns["firms"])
    ldgr.commit(rv, columns["workers"])
    return rv


def nonfirms_consumption(ldgr, dt, paB=Decimal(1), paW=Decimal(26)):
    """
    This operation is as Keen defined it, since it doesn't impact
    the loan ledger or the licence asset which Wilson introduced.

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
    """
    Run the simulation by repeating the operations described above.
    At the end of every cycle, the equality of the
    Fundamental Accounting Equation is tested. A warning is raised if
    the equality fails.

    :param samples: A sequence of times. At each of these the simulation
                    will print out the state of the Ledger. The simulation
                    will stop after the final sample time has passed.
    :param initial: The initial value of the banking licence.
    :param interval:    The value of the simulation timestep in seconds.
    :param ledger:  An existing Ledger object. If None is passed, a new
                    one will be created.
    :returns:       This routine is a generator which yields RSON_ strings.
                    The final return value is the ledger object used during
                    the simulation.
    """
    t = 0
    ldgr = ledger or Ledger(*columns.values(), ref=Cy.USD)
    cols = ldgr.columns
    yield metadata(ldgr)

    banking_licence(ldgr, initial)

    yield journal(
        ldgr, ts=t, note="Keen Money Circuit with balanced accounting")

    while samples:
        t += interval
        bank_loan(ldgr, interval),
        interest = bank_charge(ldgr, interval)
        flows = (
            firms_repayment(ldgr, interval, interest),
            nonbank_interest(ldgr, interval),
            firms_wages(ldgr, interval),
            nonfirms_consumption(ldgr, interval))

        if not ldgr.equation.status is Status.ok:
            warnings.warn(
                "# Unbalanced ledger\n{}".format(journal(ldgr)))

        if t >= samples[0]:
            yield journal(ldgr, ts=t)
            samples.pop(0)
    return ldgr


def main(args):
    warnings.simplefilter("error")
    samples = [YEAR * i for i in range(11)]
    for msg in simulate(samples, args.initial, args.interval):
        print(msg)
    return len(samples) and 1  # an error if samples not empty


def parser():
    rv = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
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
