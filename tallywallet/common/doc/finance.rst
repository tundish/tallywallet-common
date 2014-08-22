..  Titling
    ##++::==~~--''``

The time value of money
:::::::::::::::::::::::

Money is a thing which can't exist without human beings. Before
new money is made, someone somewhere has to generate its value.

In modern Western banking, that value derives from a promise to
pay. In other words, a debt of one sort or another.

In Tallywallet, debts are recorded with a promissory :py:func:`Note
<tallywallet.common.finance.Note>`. Your Python script begins like this::

    import datetime
    from decimal import Decimal

    from tallywallet.common.finance import Note

Below I'll show how to use Tallywallet to work out the value of
debt over time. The examples are taken from
`Schaum's Mathematics of Finance`, 2nd edition.


Lending
=======

We'll start off by recording the details of a historic loan. Back in
May of 1995, we lent out $1500 at an annualized interest rate of 8%.
The loan was due to be repaid 90 days later::

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

If you run this Python script now, you'll see that it came to `$1530.00`.

The :py:func:`value_simple <tallywallet.common.finance.value_simple>`
function applies when there's one interest period for the term of the note.
When the debt spans multiple interest periods, you'd calculate the value
of the note with
:py:func:`value_series <tallywallet.common.finance.value_series>`.

We'll see the flexibility of this function in a moment. For now, let's fill
out its parameters with the attributes of the promissory note to confirm
our previous answer::

    from tallywallet.common.finance import value_series

    print(list(value_series(**vars(note))))


This gives us an output of
``[(datetime.date(1995, 8, 9), Decimal('1530.0000'))]``.
 
Discounting
===========

As we recall, in the Spring of 1995 we found ourselves short of cash. We
couldn't wait for our loan to be paid, so in July we sold on the debt to
a business contact. He agreed to discount the loan at 9%.

::

        valueAtMaturity = value_simple(note)
        dateOfSale = datetime.date(1995, 7, 2)
        termRemaining = note.date + note.term - dateOfSale
        discount = Decimal("0.09")

We can use :py:func:`value_series <tallywallet.common.finance.value_series>`
to work out how much the debt is worth as cash. We start from the date of
maturity, and work back in time, supplying the discounted interest rate::

        deal = list(value_series(
            date=note.date + note.term,
            principal=valueAtMaturity,
            term=(-termRemaining),
            period=note.period,
            interest=discount)
        )

When we print out the result of the deal we get::

    [(datetime.date(1995, 7, 2), Decimal('1515.466'))]
 
Amortization
============

Now let's try something a little closer to home.

A mortgage is what happens when interest is allowed to compound against
a loan. The creditor demands regular payments, but to begin with they
mostly go to supply interest on the debt; they hardly pay off the principal
at all. Slowly, according to a process of `amortization`, the surplus
to interest reduces what's owing.

Tallywallet can construct a complete amortization schedule for this kind
of debt.

Here's an example. A debt of $6000 with interest at 16% compounded twice
every year is to be amortized by equal semiannual payments over the next 3
years, the first payment due in 6 months.


::

    from tallywallet.common.finance import schedule

    now = datetime.datetime.utcnow()
    loan = Note(
        date=now,
        principal=6000,
        currency="$",
        term=datetime.timedelta(days=360*3),
        interest=Decimal("0.16"),
        period=datetime.timedelta(days=180)
    )

    plan = list(schedule(loan, places=0))

You'll find `plan` to be a sequence of objects, each specifying the
amount and date of payment, along with how that's to be shared between
interest and debt. The remaining balance is also calculated::

    [
        Amortization(
            date=datetime.datetime(2015, 2, 17, 16, 5, 20, 0),
            payment=Decimal('1298'),
            interest=Decimal('480.000'),
            repaid=Decimal('818.000'),
            balance=Decimal('5182.000')
        ),
        Amortization(
            date=datetime.datetime(2015, 8, 16, 16, 5, 20, 0),
            payment=Decimal('1298'),
            interest=Decimal('414.560000'),
            repaid=Decimal('883.440000'),
            balance=Decimal('4298.560000')
        ),
        Amortization(
            date=datetime.datetime(2016, 2, 12, 16, 5, 20, 0),
            payment=Decimal('1298'),
            interest=Decimal('343.884800000'),
            repaid=Decimal('954.115200000'),
            balance=Decimal('3344.444800000')
        ),
        Amortization(
            date=datetime.datetime(2016, 8, 10, 16, 5, 20, 0),
            payment=Decimal('1298'),
            interest=Decimal('267.555584000000'),
            repaid=Decimal('1030.444416000000'),
            balance=Decimal('2314.000384000000')
        ),
        Amortization(
            date=datetime.datetime(2017, 2, 6, 16, 5, 20, 0),
            payment=Decimal('1298'),
            interest=Decimal('185.120030720000000'),
            repaid=Decimal('1112.879969280000000'),
            balance=Decimal('1201.120414720000000')
        ),
        Amortization(
            date=datetime.datetime(2017, 8, 5, 16, 5, 20, 0),
            payment=Decimal('1297.210047897600000000'),
            interest=Decimal('96.089633177600000000'),
            repaid=Decimal('1201.120414720000000000'),
            balance=Decimal('0')
        )
    ]

