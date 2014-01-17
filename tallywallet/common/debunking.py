#!/usr/bin/env python3
#   encoding: UTF-8

import argparse
from collections import Counter
from decimal import Decimal
import logging
from pprint import pprint
import random
import statistics
import sys
import unittest
 
__doc__ = """
'Debunking Economics' 2nd Ed 2011 Steve Keen. Page 363, Para 107.

NB: see http://en.wikipedia.org/wiki/Annual_percentage_rate

Vault starts with $100 million
Sim runs for 10 years

Vault:  16.9 million
Owing:  83.1 million
Safe:   2.7 million
Firms:  72.1 million
Workers:8.3 million
"""

__all__ = [
    "HOUR", "DAY", "WEEK", "YEAR",
    "bank_loan", "bank_charge",
    "firms_interest", "firms_repay", "firms_wages", "nonfirms_consume"
]

SEC = 1
HOUR = 60 * 60 * SEC
DAY = 24 * HOUR
WEEK = 7 * DAY
YEAR = 52 * WEEK

def bank_loan(ldgr, dt, pa=Decimal("0.5")):
    rv = ldgr["vault"] * pa * Decimal(dt / YEAR)
    ldgr["vault"] -= rv
    ldgr["firms"] += rv
    ldgr["owing"] += rv
    return rv 

def bank_charge(ldgr, dt, pa=Decimal("5E-2")):
    rv = ldgr["owing"] * pa * Decimal(dt / YEAR)
    ldgr["safe"] += rv
    ldgr["firms"] -= rv
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


def main(args):
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)-7s %(name)s|%(message)s")

    log = logging.getLogger("tallywallet.dynamics.debunking")

    t = 0
    picks = [DAY, YEAR, 10 * YEAR]
    ldgr = Counter(vault=int(100E6))
    interval = HOUR
    while picks:
        t += interval
        flows = (
            bank_loan(ldgr, interval),
            bank_charge(ldgr, interval),
            firms_interest(ldgr, interval),
            firms_wages(ldgr, interval),
            nonfirms_consume(ldgr, interval),
            firms_repay(ldgr, interval))

        # report
        if t >= picks[0]:
            log.info(t)
            pprint(ldgr)
            picks.pop(0)


def parser():
    rv = argparse.ArgumentParser(description=__doc__)
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
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
