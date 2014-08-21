..  Titling
    ##++::==~~--''``

The time value of money
:::::::::::::::::::::::

Money is a thing which can't exist without human beings. Before
new money is made, someone somewhere has to generate its value.

In modern Western banking, that value derives from a promise to
pay. In other words, a loan of one sort or another.

Here we'll show how to use Tallywallet to work out the value of
debt over time. The examples are taken from
`Schaum's Mathematics of Finance`, 2nd edition.

In Tallywallet, loans are recorded with a promissory :py:func:`Note
<tallywallet.common.finance.Note>`. So begin your code like this::

    import datetime
    from decimal import Decimal

    from tallywallet.common.finance import Note



Lending
=======

We'll start off by recording the details of a historic loan. Back in
in May of 1995, we lent out $1500 at an annualized interest rate of 8%.
The loan was due to repaid 90 days later::

    note = Note(
        date=datetime.date(1995, 5, 11),
        principal=1500,
        currency="$",
        term=datetime.timedelta(days=90),
        interest=Decimal("0.08"),
        period=datetime.timedelta(days=360)
    )

What was the `simple value` of this promise on maturity?::


    from tallywallet.common.finance import value_simple

    print(value_simple(note))

If you run this Python script now, you'll see that it came to $1530.00.


Discounting
===========

Amortization
============

