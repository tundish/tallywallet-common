:Copyright: 2013 Thuswise Ltd

..  Titling
    ##++::==~~--''``

Installation
::::::::::::

::

    python3.4 setup.py install
    python3.4 -m unittest discover tallywallet

Issues
::::::

https://www.assembla.com/spaces/tallywallet/tickets

Notes
:::::
W
M

Participants pay a fee to engage in discussion. On meeting they are issued WellMet currency.
The fee they pay may be in cash or WM.
If cash, a proportion of the sum is used to guarantee the WM against redemptions.
WellMet currency may be redeemed for cash.

Wellmet currency is depreciated by a defined profile from the point it is
reified.

Fundamental Accounting Equation
===============================

Assets - Liabilities = Capital + Income - Expenses

Exchange
========

Gains are income, losses are expenses.

`Adjusted cost base`
ISO 4217 currency codes

Design Thoughts
===============

Consider 1 SQLite db per account, then attach base tables db.

..  _Tutorial on multiple currency accounting: http://www.mscs.dal.ca/~selinger/accounting/
