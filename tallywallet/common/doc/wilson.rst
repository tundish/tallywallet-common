..  Titling
    ##++::==~~--''``

A simple Keen Monetary Circuit simulation
:::::::::::::::::::::::::::::::::::::::::

Economic crises have become frequent events in the last 80 years. The
character and origins of each are difficult to comprehend. The
lack of a coherent narrative to explain them has led to controversy in
the academic profession as rival schools challenge or defend the
orthodoxy of neoclassical economic theory.

Debunking economics
===================

One longstanding opponent of neoclassical theory, an Australian professor
called `Steve Keen`_, wrote a book called
`Debunking economics: The naked Emperor dethroned?` (the reference for
this example is the 2011 edition, particularly chapters 13-18).

Keen painstakingly exposed the deficiencies of orthodox macroeconomic theory.
As an Engineer familiar with the mathematics
of electronic control systems, he presented an alternative; to treat the
economy as a natural system capable of dynamic instability.

Chapters 13-18 provide reference material for the implementation of
this software. Professor Keen presents a top-down synthesis of Marx,
Schumpeter, Keynes and Minsky. But he also acknowledges the validity
of a multi-agent paradigm which is the approach of
`tallywallet-dynamics`.

The Double-entry paradigm
=========================

`Double entry view on Keen Circuit Model`_ (2012)

    `Neil Wilson`_ reviews Keen's dynamic circuit model. He proposes some
    modifications to make it more recognisable to a reader familiar with
    double-entry accounting.

Efficiency
==========

A purely numerical simulation would use `collections.Counter`.
Ledger better when complex accounting strategies are computed at run-time
and assurance is needed of balanced equation. Also, hands-off simulation
(parallelised Monte Carlo/parameter sweep) when there might be so many
scenarios that they cannot be checked manually for correctness.

    Wilson's description of the model is re-documented here as this table.

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

.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _compile Python 3.4: http://www.python.org/download/source/
.. _tallywallet-common: https://pypi.python.org/pypi/tallywallet-common
.. _David Orrell: http://www.postpythagorean.com
.. _Steve Keen: http://www.debtdeflation.com/blogs
.. _Double entry view on Keen Circuit Model: http://www.3spoken.co.uk/2011/12/double-entry-view-on-keen-circuit-model.html
.. _Neil Wilson: http://www.3spoken.co.uk
.. _Fred Decker: http://www.modernmt.net
