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

There are some scenarios where Tallywallet's features do apply to
economics. Here is one.

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

Debunking.py
~~~~~~~~~~~~

.. automodule:: tallywallet.common.debunking
   :members:

.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _compile Python 3.4: http://www.python.org/download/source/
.. _tallywallet-common: https://pypi.python.org/pypi/tallywallet-common
.. _David Orrell: http://www.postpythagorean.com
.. _Steve Keen: http://www.debtdeflation.com/blogs
.. _Double entry view on Keen Circuit Model: http://www.3spoken.co.uk/2011/12/double-entry-view-on-keen-circuit-model.html
.. _Neil Wilson: http://www.3spoken.co.uk
.. _Fred Decker: http://www.modernmt.net
