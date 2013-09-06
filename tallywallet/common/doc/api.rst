..  Titling
    ##++::==~~--''``

Programming API
:::::::::::::::

Currency
========

.. automodule:: tallywallet.common.currency
   :members: Currency

Trade
=====

.. autoclass:: tallywallet.common.trade.TradePath
   :member-order: bysource

.. autoclass:: tallywallet.common.trade.TradeGain
   :member-order: bysource

Exchange
========

.. automodule:: tallywallet.common.exchange
   :members: Exchange

Ledger
======

.. automodule:: tallywallet.common.ledger
   :members: Role

.. autoclass:: tallywallet.common.ledger.Column
   :member-order: bysource

.. autoclass:: tallywallet.common.ledger.Ledger
   :members:
   :member-order: bysource

Example
:::::::

This example is taken from `Peter Selinger's tutorial`_ on multiple currency
accounting. We'll use a Ledger to track the transactions set out below,
which comprise both actual expenses and incurred gains/losses due to variations
in currency rates.

The scenario is a brief trip from Canada to the USA, which requires buying US
dollars, spending some during exchange rate fluctuations, and changing back
to Canadian money at the end.

=====   =============== ======= ======= ======= ======= ===============
date                    asset   asset   capital expense trading
=====   =============== ======= ======= ======= ======= ===============
Jan 1   Opening balance CAD 200 USD 0   CAD 200 CAD 0   USD 0 CAD 0
Jan 2   1 USD==1.20CAD  CAD-120 USD 100    .       .    USD 100 CAD 120
 .      Balance         CAD 80  USD 100 CAD 200 CAD 0   USD 100 CAD 120
Jan 3   1 USD==1.30CAD     .    USD-40     .    CAD 52  USD-40 CAD 52
 .      Balance         CAD 80  USD 60  CAD 200 CAD 52  USD 60 CAD-68
Jan 5   1 USD==1.25CAD  CAD 75  USD-60     .       .    USD-60 CAD 75
 .      Balance         CAD 155 USD 0   CAD 200 CAD 52  USD 0  CAD 07
Jan 7   Buy food        CAD-20     .       .    CAD 20     .      
 .      Balance         CAD 135 USD 0   CAD 200 CAD 72  USD 0  CAD 07
=====   =============== ======= ======= ======= ======= ===============

Throughout, we'll assume this boilerplate::

    import datetime
    from decimal import Decimal as Dl
    from tallywallet.common.currency import Currency as Cy
    from tallywallet.common.ledger import Ledger
    from tallywallet.common.ledger import Role

Jan 1
=====

First, we'll establish a ledger with the necessary columns. We needn't
define a currency trading account; that will be created for us::

    ldgr = Ledger(
        Column("Canadian cash", Cy.CAD, Role.asset),
        Column("US cash", Cy.USD, Role.asset),
        Column("Capital", Cy.CAD, Role.capital),
        Column("Expense", Cy.CAD, Role.expense),
        ref=Cy.CAD)

At this point, there's no balance, and no rates defined for the currencies.
``ldgr.equation.status`` will evaluate to ``Status.failed``.

The scenario begins with an opening balance of CAD 200. In double entry
book-keeping, this becomes an asset on the left hand side, and capital on the
right. We can define the opening balance like this::

    for amount, col in zip(
        (Dl(200), Dl(0), Dl(200), Dl(0)), ldgr.columns.values()
    ):
        ldgr.commit(
            amount, col,
            ts=datetime.date(2013, 1, 1), note="Opening balance")

Jan 2
=====

Let's apply the initial currency exchange rate. We do that by instantiating an
Exchange object, and creating a sequence of trades to apply to our ledger::

    exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.2")})
    for args in ldgr.adjustments(exchange):
        ldgr.commit(
            *args, ts=datetime.date(2013, 1, 2),
            note="1 USD = 1.20 CAD")

The next step is to buy CAD 120 worth of US dollars. How many USD will that
give us?::

    usd = exchange.convert(120, TradePath(Cy.CAD, Cy.CAD, Cy.USD))

So we add that to our US cash account::

    ldgr.commit(usd, ldgr.columns["US cash"])

If we should check ``ldgr.equation.status`` we'd get ``Status.failed``.
Our book is unbalanced. We must remember to deduct from our Canadian cash::

    ldgr.commit(-120, ldgr.columns["Canadian cash"])

And now, ``ldgr.equation.status`` will evaluate to ``Status.ok``.

Jan 3
=====

Our book holds both American and Canadian dollars, so it's exposed to
fluctuations in the exchange rate. On 3rd January, you can get $1.30 Canadian
for one American greenback. Let's apply that to our ledger::

    exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.3")})
    for args in ldgr.adjustments(exchange):
        ldgr.commit(
            *args, ts=datetime.date(2013, 1, 3),
            note="1 USD = 1.30 CAD")

At this point in the story, we spend forty US dollars. On the left hand side of
the ledger, it's clear that this needs to come from our US assets. But on the
right hand side, our expense account is in Canadian dollars. So we need to make
a calculation to determine how much to deduct from there::

    cad = exchange.convert(40, TradePath(Cy.USD, Cy.CAD, Cy.CAD))

And so::

    ldgr.commit(-40, ldgr.columns["US cash"])
    ldgr.commit(cad, ldgr.columns["Expense"])

Jan 5
=====

The exchange rate shifts a bit today in favour of the Canadian dollar. We don't
make any purchases, but we do convert all our US dollars back to Canadian. So
there should be no change to the right hand side of our ledger, only movement
of our assets on the left.

First we apply the new rate::

    exchange = Exchange({(Cy.USD, Cy.CAD): Dl("1.25")})
    for args in ldgr.adjustments(exchange):
        ldgr.commit(
            *args, ts=datetime.date(2013, 1, 5),
            note="1 USD = 1.25 CAD")

... then work out how much our US dollars are worth::

    usd = ldgr.value("US cash")
    cad = exchange.convert(usd, TradePath(Cy.USD, Cy.CAD, Cy.CAD))

... and finish by committing that to our book::

    ldgr.commit(-usd, ldgr.columns["US cash"])
    ldgr.commit(cad, ldgr.columns["Canadian cash"])

Jan 7
=====

We are now back in Canada but stuck in the airport waiting for our transfer
home. We want food. So we cough up twenty dollars for a nasty burger and a
bottle of fizzy beer. Here's the transaction for that::

    ldgr.commit(-20, cols["Canadian cash"], note="Buy food")
    ldgr.commit(20, cols["Expense"], note="Buy food")

How much money do we have left? ``ldgr.value("Canadian cash")`` says $135.00.
Looking at the other columns it seems we spent CAD 72.00 during our trip. We
accidentally made CAD 7.00 due to the fluctuations in the exchange rate while
we were away.

..  _Peter Selinger's tutorial: http://www.mscs.dal.ca/~selinger/accounting/
