#!/usr/bin/env python3
#   encoding: UTF-8

import argparse
from collections import Counter
from decimal import Decimal
import logging
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
    "simulate"
]

SEC = 1
HOUR = 60 * 60 * SEC
DAY = 24 * HOUR
WEEK = 7 * DAY
YEAR = 52 * WEEK

def bank_loan(ldgr, dt, pa=Decimal("0.5")):
    rv = ldgr.value("vault") * pa * Decimal(dt / YEAR)
    ldgr.commit(-rv, ldgr.columns["vault"])
    ldgr.commit(rv, ldgr.columns["firms"])
    ldgr.commit(rv, ldgr.columns["owing"])
    return rv 

def bank_charge(ldgr, dt, pa=Decimal("5E-2")):
    rv = ldgr.value("owing") * pa * Decimal(dt / YEAR)
    ldgr.commit(rv, ldgr.columns["safe"])
    ldgr.commit(-rv, ldgr.columns["firms"])
    return rv

def firms_interest(ldgr, dt, pa=Decimal("2E-2")):
    rv = ldgr["firms"] * pa * Decimal(dt / YEAR)
    ldgr["safe"] -= rv
    ldgr["firms"] += rv
    return rv

def firms_wages(ldgr, dt, pa=Decimal(3)):
    rv = ldgr["firms"] * pa * Decimal(dt / YEAR)
    ldgr["firms"] -= rv
    ldgr["workers"] += rv
    return rv

def nonfirms_consume(ldgr, dt, paB=Decimal(1), paW=Decimal(26)):
    banks = ldgr["safe"] * paB * Decimal(dt / YEAR)
    workers = ldgr["workers"] * paW * Decimal(dt / YEAR)
    ldgr["safe"] -= banks
    ldgr["workers"] -= workers
    ldgr["firms"] += (banks + workers)
    return banks + workers

def firms_repay(ldgr, dt, pa=Decimal("0.1")):
    rv = ldgr["owing"] * pa * Decimal(dt / YEAR)
    ldgr["firms"] -= rv
    ldgr["vault"] += rv
    ldgr["owing"] -= rv
    return rv


def simulate(interval, samples):
    t = 0
    #ldgr = Counter(vault=int(100E6))
    ldgr = Ledger(
        Column("vault", Cy.USD, Role.asset),
        Column("safe", Cy.USD, Role.asset),
        Column("owing", Cy.USD, Role.capital),
        Column("firms", Cy.USD, Role.expense),
        Column("workers", Cy.USD, Role.expense),
        ref=Cy.USD)

    while samples:
        t += interval
        flows = (
            bank_loan(ldgr, interval),
            bank_charge(ldgr, interval),
            firms_interest(ldgr, interval),
            firms_wages(ldgr, interval),
            nonfirms_consume(ldgr, interval),
            firms_repay(ldgr, interval))

        # report
        if t >= samples[0]:
            yield repr(ldgr)
            samples.pop(0)
    return ldgr


def main(args):
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)-7s %(name)s|%(message)s")

    log = logging.getLogger("tallywallet.common.debunking")
    samples = [YEAR * i for i in range(11)]
    simulate(args.interval, samples)
    return len(samples) and 1  # an error if samples not empty

def parser():
    rv = argparse.ArgumentParser(description=__doc__)
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    rv.add_argument(
        "--interval", type=int, default=HOUR,
        help="Writes each data point on a separate line")
    rv.add_argument(
        "--lineout", action="store_true", default=False,
        help="Writes each data point on a separate line")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
