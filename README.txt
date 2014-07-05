..  Titling
    ##++::==~~--''``

Tallywallet helps Engineers understand Money and Banking.

You can use it to create economic simulations, or to enable your applications
with currency exchange and accounting features.

This package
::::::::::::

Tallywallet is a very young project. This package implements the following:

* A Ledger class for double-entry accounting
* An Exchange class to enable currency trading
* `Pre-hoc` calculation of exchange rate gains on currency trading accounts
* Evaluation of the Fundamental Accounting Equation to verify balanced accounts
* A text format for saving Ledgers to file
* A tutorial on how to achieve foreign currency exchange in Python code
* An example of a macroeconomic monetary circuit simulation

Requirements
::::::::::::

Tallywallet requires Python 3.4. It uses setuptools_ for installation, but
normally it has no external runtime dependencies.

You may have to `compile Python 3.4`_ yourself if it is not yet available from
your package repository.

Tallywallet comes with unit tests. To run them all requires the RSON_ package.

Quick start
:::::::::::

Download and unpack the source distribution::

    $ tar -xzvf tallywallet-common-0.007.tar.gz
    $ cd tallywallet-common-0.007

Run the tests::

    $ python3.4 -m unittest discover tallywallet

Consult the documentation::

    $ firefox tallywallet/common/doc/html/index.html

Roadmap
:::::::

Tallywallet's mission is to provide a validated Pythonic framework for money
trading and economic applications.

It is developed by a private individual but released to the public under the
`GNU Affero General Public License`_.

The API may change significantly as the project proceeds. At this early stage,
you should only use the latest release, which may not be compatible with
previous versions.

Next release
============

The next release will provide an example of a macro-economic simulation using
balanced accounting methods.

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
.. _compile Python 3.4: http://www.python.org/download/source/
.. _GNU Affero General Public License: http://www.gnu.org/licenses/agpl-3.0.html
.. _message board: https://www.assembla.com/spaces/tallywallet/messages
