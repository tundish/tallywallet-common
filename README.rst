..  Titling
    ##++::==~~--''``

Tallywallet helps Engineers understand Money and Banking.

You can use it to create economic simulations, or to enable your applications
with currency exchange and accounting features.

This package
::::::::::::

Tallywallet is a very young project. This package implements the following:

Code
====

* Functions to work with Promissory Notes
* A Ledger class for double-entry accounting
* An Exchange class to enable currency trading
* `Pre-hoc` calculation of exchange rate gains on currency trading accounts
* Evaluation of the Fundamental Accounting Equation to verify balanced accounts
* A text format for saving Ledgers to file

Documentation
=============

* A how-to on loans, discounting, and amortization
* A tutorial on how to achieve foreign currency exchange in Python code
* An example of a macroeconomic monetary circuit simulation

Requirements
::::::::::::

Tallywallet requires Python 3. It uses setuptools_ for installation, but
normally it has no external runtime dependencies.

Tallywallet comes with unit tests. To run them all requires the RSON_ package.

Quick start
:::::::::::

Clone the git repository::

    git clone git@github.com:tundish/tallywallet-common.git
    cd tallywallet-common

Install the package and its dependencies::

    python3 -m pip install .[docbuild,test]

Run the tests::

    python3 -m unittest discover tallywallet

Consult the documentation::

	sphinx_build tallywallet/common/doc tallywallet/common/doc/html
    firefox tallywallet/common/doc/html/index.html

Roadmap
:::::::

Tallywallet's mission is to provide a validated Pythonic framework for money
trading and economic applications.

It is developed by a private individual but released to the public under the
`GNU Affero General Public License`_.

The API may change significantly as the project proceeds. At this early stage,
you should only use the latest release, which may not be compatible with
previous versions.

Can you help?
=============

* If you've spotted a bug in Tallywallet, please let us know so we can fix it.
* If you think Tallywallet lacks a feature, you can help drive development by describing
  your Use Case.

In either event, please leave a message on the project's `message board`_.


:Author: D Haynes
:Copyright: 2014 Thuswise Ltd

.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _RSON: https://pypi.python.org/pypi/rson
.. _GNU Affero General Public License: http://www.gnu.org/licenses/agpl-3.0.html
.. _message board: https://www.assembla.com/spaces/tallywallet/messages
