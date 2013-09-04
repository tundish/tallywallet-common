..  Titling
    ##++::==~~--''``

Tallywallet helps Engineers understand Money and Banking.

You can use it to create economic simulations, or to provide your applications
with currency exchange and accounting features.

This release
::::::::::::

Tallywallet is a very young project. This release contains the following:

* A Ledger class for double-entry accounting
* An Exchange class to enable currency trading
* `Pre-hoc` calculation of exchange rates on currency trading accounts
* Evaluation of the Fundamental Accounting Equation to verify balanced accounts

Installation
::::::::::::

Tallywallet requires Python 3.4. It uses setuptools for installation, but
has no external runtime dependencies.

You may have to compile Python 3.4 yourself if it is not yet available from
your package repository.::

    tar -xzvf tallywallet-common-0.001.tar.gz
    python3.4 -m unittest discover tallywallet

    python3.4 setup.py install

Roadmap
:::::::

Tallywallet's mission is to provide a validated Pythonic framework for money
trading and economic applications.

It is developed by a private individual but released to the public under the
`GNU Affero General Public License`_.

The API may change significantly as the project proceeds. At this early stage,
you should only use the latest release, which may not be compatible with
previous versions.

If you think it lacks a feature, you can help drive development by describing
your Use Case

.. _GNU Affero General Public License: http://www.gnu.org/licenses/agpl-3.0.html
https://www.assembla.com/spaces/tallywallet/tickets
http://www.python.org/download/source/

:Author: D Haynes
:Copyright: 2013 Thuswise Ltd


..  _Tutorial on multiple currency accounting: http://www.mscs.dal.ca/~selinger/accounting/
