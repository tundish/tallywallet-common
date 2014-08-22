..  Titling
    ##++::==~~--''``

API Reference
:::::::::::::

Currency
========

.. automodule:: tallywallet.common.currency
   :members: Currency

Finance
========

.. autoclass:: tallywallet.common.finance.Note
   :member-order: bysource

The functions of the Finance module are all intended to be compatible with
the :py:class:`Note <tallywallet.common.finance.Note>` type. They either take
such an object as a parameter, or their keyword arguments can be supplied from
the result of the `vars` function on a
:py:class:`Note <tallywallet.common.finance.Note>` object.

.. automodule:: tallywallet.common.finance
   :members: value_simple, value_series, discount_simple, schedule

.. autoclass:: tallywallet.common.finance.Amortization
   :member-order: bysource

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

Output
======

.. automodule:: tallywallet.common.output
   :members:
   :member-order: bysource

