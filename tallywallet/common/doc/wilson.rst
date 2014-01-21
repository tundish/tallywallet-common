..  Titling
    ##++::==~~--''``

A simple Keen Monetary Circuit simulation
:::::::::::::::::::::::::::::::::::::::::

Why you shouldn't use Tallywallet in an economic simulation...
==============================================================

Book-keeping is a contemplative activity which usually requires a
human being to make judgements on how best to present accounts.

A numerical simulation of an economy is a different thing. You want it
to go as fast as it can, and to optimise for speed is to do away with
such features as balanced accounting.

So, while Tallywallet's `Ledger` class is designed for interactive use,
a computational simulation in Python would most likely choose
`collections.Counter` to store numerical values.

...and why you might do
=======================

But there are some scenarios where Tallywallet's features could aid in
simulation. Here is one.

Debunking economics
~~~~~~~~~~~~~~~~~~~

Economic crises have become frequent events in the last 80 years. The
lack of a coherent narrative to explain them has led to controversy in
the academic profession as rival schools challenge or defend the
orthodoxy of neoclassical economic theory.

One longstanding opponent of neoclassical theory, an Australian professor
called `Steve Keen`_, wrote a book called
`Debunking economics: The naked Emperor dethroned?` (the reference for
this example is the 2011 edition, particularly chapters 13-18).

As an Engineer familiar with the mathematics of electronic control systems,
Keen saw many deficiencies in the static approach of neoclassical
macroeconomics. He presented an alternative; to treat the economy as a natural
system capable of dynamic instability.

Professor Keen incorporated ideas from Marx, Schumpeter, Keynes and Minsky,
to create what he called the `Monetary Circuit Model`. Far from being
complicated, this approach feels quite natural to someone who has written
software to simulate industrial processes.

Keen's simulation uses simple rules but is nonetheless capable of predicting
the kind of phenomena seen in financial downturns. These are not explained
by orthodox economic models.

Double-entry paradigm
~~~~~~~~~~~~~~~~~~~~~

In 2012, the UK-based blogger `Neil Wilson`_ wrote a critique of Keen's new
model. Wilson was concerned that Keen's work had too much Engineering about
it.

While supportive of the approach, Wilson felt that the model's ignorance of
accounting concepts prevented its acceptance by the financial community.

In the article `Double entry view on Keen Circuit Model`_, Wilson reviews
Keen's dynamic circuit model. He proposes some modifications to make it more
recognisable to a reader familiar with the double-entry accounting system
used by banks and businesses.

Ledger simulation example
=========================

This example will use Tallywallet to recreate Keen's simulation. But we'll
also incorporate Wilson's recommendations to maintain a balanced ledger.

Wilson's description of the model is captured here in this table.

.. Small screens may need an 8 point font to see this table one row per line.

+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
|       |                                       |   Bank assets                                 |   Bank liabilities                                                            |   Bank equity             |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| ID    |   Operation                           |   Licence value       |   Loan ledger         |   Vault               |   Firms                   |   Workers                 |   Safe                    |
+=======+=======================================+=======================+=======================+=======================+===========================+===========================+===========================+
| 01    |   Grant Licence                       |   |+| Licence value   |                       |   |-| Licence value   |                           |                           |                           |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 02    |   Lend Money                          |                       |                       |   |+| Lend money      |   |-| Lend money          |                           |                           |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 03    |   Record loan                         |   |-| Lend money      |   |+| Lend money      |                       |                           |                           |                           |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 04    |   Charge Interest                     |                       |                       |   |+| Interest charge |                           |                           |   |-| Interest charge     |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 05    |   Record Interest                     |   |-| Interest charge |   |+| Interest charge |                       |                           |                           |                           |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 06    |   Repay Loan and Interest             |                       |                       |   |-| Loan repayment  |   |+| Loan repayment      |                           |                           |
+-------+                                       |                       |                       |                       |                           |                           |                           |
|       |                                       |                       |                       |   |-| Interest charge |   |+| Interest charge     |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 07    |   Record Loan and Interest Repayment  |   |+| Loan repayment  |   |-| Loan repayment  |                       |                           |                           |                           |
+-------+                                       |                       |                       |                       |                           |                           |                           |
|       |                                       |   |+| Interest charge |   |-| Interest charge |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 08    |   Pay Firm Deposit Interest           |                       |                       |                       |   |-| Firm interest       |                           |   |+| Firm interest       |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 09    |   Pay Worker Deposit Interest         |                       |                       |                       |                           |   |-| Worker interest     |   |+| Worker interest     |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 10    |   Hire Workers                        |                       |                       |                       |   |+| Pay workers         |   |-| Pay workers         |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 11    |   Workers' Consumption                |                       |                       |                       |   |-| Workers' consumption|   |+| Workers' consumption|                           |
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+
| 12    |   Bankers' Consumption                |                       |                       |                       |   |-| Bankers' consumption|                           |   |+| Bankers' consumption|
|       |                                       |                       |                       |                       |                           |                           |                           |
+-------+---------------------------------------+-----------------------+-----------------------+-----------------------+---------------------------+---------------------------+---------------------------+


.. |+| replace:: **+**
.. |-| replace:: **-**

How it works
~~~~~~~~~~~~

.. automodule:: tallywallet.common.debunking
   :members:
   :member-order: bysource

Typical output
~~~~~~~~~~~~~~

By default the program replicates the behaviour described in `Debunking`.
It begins with a debt supply of $100,000,000 and runs for ten years.
The output matches to three significant figures that published by Keen.

::

    {}
        header:version: 0.005
    {}
        ledger:columns:    [
                [licence, USD, asset],
                [loans, USD, asset],
                [vault, USD, liability],
                [firms, USD, liability],
                [workers, USD, liability],
                [safe, USD, income],
                [USD trading account, USD, trading]
            ]
        ledger:ref: USD

    {}
        note:
            Keen Money Circuit with balanced accounting
        ts:
            0
    [ 100000000.00, 0.00, 100000000.00, 0.00, 0.00, 0.00, 0.00]

    {}
        ts:
            3600
    [ 99994276.62, 5723.38, 99994276.62, 5721.40, 1.96, 0.02, 0.00]

    {}
        ts:
            31449600
    [ 62400370.51, 37599629.49, 62400370.51, 33389071.04, 3733551.18, 477007.26, 0.00]

    {}
        ts:
            62899200
    [ 41765575.22, 58234424.78, 41765575.22, 51200784.95, 5832702.36, 1200937.47, 0.00]

    {}
        ts:
            94348800
    [ 30441134.47, 69558865.53, 30441134.47, 60821254.87, 6966230.99, 1771379.68, 0.00]

    {}
        ts:
            125798400
    [ 24226245.65, 75773754.35, 24226245.65, 66043064.02, 7581387.75, 2149302.57, 0.00]

    {}
        ts:
            157248000
    [ 20815495.07, 79184504.93, 20815495.07, 68887106.37, 7916392.69, 2381005.88, 0.00]

    {}
        ts:
            188697600
    [ 18943664.38, 81056335.62, 18943664.38, 70439795.64, 8099272.33, 2517267.65, 0.00]

    {}
        ts:
            220147200
    [ 17916397.80, 82083602.20, 17916397.80, 71288870.80, 8199273.09, 2595458.32, 0.00]

    {}
        ts:
            251596800
    [ 17352630.66, 82647369.34, 17352630.66, 71753705.00, 8254017.40, 2639646.94, 0.00]

    {}
        ts:
            283046400
    [ 17043233.47, 82956766.53, 17043233.47, 72008380.09, 8284010.14, 2664376.30, 0.00]

    {}
        ts:
            314496000
    [ 16873435.32, 83126564.68, 16873435.32, 72147986.47, 8300451.11, 2678127.10, 0.00]

.. _Steve Keen: http://www.debtdeflation.com/blogs
.. _Double entry view on Keen Circuit Model: http://www.3spoken.co.uk/2011/12/double-entry-view-on-keen-circuit-model.html
.. _Neil Wilson: http://www.3spoken.co.uk
.. _RSON: http://code.google.com/p/rson/

