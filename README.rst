==========
Pythia doc
==========

------------
Installation
------------

Python
======

Pythia uses poetry for package installation. You need to `install poetry <https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions>`_ before installing the packages.

I also recommend using a virtualenv for the project. After you have poetry installed and the
virtualenv active, just run::

    poetry install

in the root pythia directory.


Javascript/Vue
==============

The Vue source is in the `design/pythia-ui` directory. From that directory, running `yarn install`
should install all the necessary packages. BTW, I use npm version 6.14.12.


---------------------------
Running in development mode
---------------------------

Python
======

The python server is configure using standard Django config files located in the `config/settings`
directory. However, it is best to configure it using `.env` files or env variables as it uses
the `decouple` library to make the settings more flexible.

A sample `.env` file is located in the `.env.example` file in the root directory, so just doing::

    cp .env.example .env

will give you a working `.env` file to use.

When running the javascript development server, it expects to find the backend on the
`localhost:8018` address. Therefore it is necessary to start the Python dev server at this port::

    python manage.py runserver localhost:8018


Javascript
==========

The javascript development server is started from the `design/pythia-ui` directory. Just run::

    yarn serve

and it will start a development frontend server with hot-reloading on `localhost:8082`. If you do
not like the port, you can change it by using the `DEV_SERVER_PORT` env variable::

    DEV_SERVER_PORT=8080 yarn serve

will run on port 8080.


Pre-commit
==========

We use a few tools to help us to commit only "good stuff". Most importantly, we use
`pre-commit <https://pre-commit.com/>`_.
It adds hooks to git so that each commit is checked against some rules. To activate it, you just
need to do::

    pre-commit install

the first time you start committing on a new machine.


Python formatting - black
=========================

One of things that pre-commit checks is the formatting of Python code using
`black <https://github.com/psf/black>`_. We reformat all Python code in our repo, even generated stuff
like migrations. It can be used from the command line by simply giving it files or directories to
reformat. It can also be integrated into PyCharm `like this <https://godatadriven.com/blog/partial-python-code-formatting-with-black-pycharm/>`_ (important is only the first part
of the article, you can ignore the stuff about partial formatting).


Javascript formatting - prettier
================================

For Javascript I found out that I like to have my code formatted using
`prettier <https://prettier.io/>`_. It is installed as part of the javascript dependencies and
has great integration into PyCharm out of the box - you just have to activate it.

Javascript formatting is not enforced by pre-commit, but we might decide to do so in the future.
It definitely helps with merges, etc.


----
Apps
----

Aleph
=====

This app contains raw data as imported from the libraries catalogue (called Aleph). It is by
design very simple - all data are in one JSONField, so that we do not have to manipulate the data.
To understand the data, you need to know the MARC21 standard.

It serves as an intermediate storage between the import and the rest of the application. It can
also be used to retrieve data about books which are not converted into other models.

Bookrank
========

The original idea of this application was to create something similar to pagerank, but for books.
But from that idea, only the name remained :)

Models
------

``WorkSet``
  There can be more than one set of books which we might want to analyze separately - for example
  the printed books in the library itself and e-books offered online. That is why all the ``Works``
  are connected to a ``WorkSet``

``Work``
  Represents one book or similar "work". It contains the data from the `Aleph` model, but processed
  into a more structured form. Not all fields from `Aleph` are converted, only those we need.

``ExplicitTopic``
  A topic can be anything assigned to a ``Work`` - some category like "children's book", but also
  a language, author, etc. All these behave very similarly, but in order to make querying simpler
  and also faster, we use specific models for each type of topic. This is why there is the abstract
  ``ExplicitTopic`` model and child models like ``Author``, ``Language``, etc.


Candidates
==========

This app was created to collect information about candidates for purchase. This means that it would
contain all the books that are now on the market and which could be potentially recommended for
buying.

The app was created in haste and it is more of a stub than a complete app.


Core
====

We use an app called ``core`` to contain models that are used throughout the code. Most importantly
a custom ``User`` model.


Hits
====

Stores data related to interest in a ``Work``, such as loans, etc.
This is the second major app together with ``bookrank`` which forms the core of the system.

Models
------

``HitType``
  Type of "interest" or "hit", such as "presence loan" (when someone borrows a book only inside
  the library and then puts is back), "absence loan" (when they take it home), "online download",
  etc.

``WorkHit``
  Records how many times a ``Work`` was "hit" (lent, downloaded) on a specific date.


Importers
=========

This is not a complete django app, but rather a python module for importing data from different
formats. It currently implements partial import of the
`Onix format <https://www.editeur.org/15/Archived-Previous-Releases/>`_.

The idea is to have all the handling of external formats in one place. It should also contain
code related to data cleanup and normalization, such as normalization of ISBNs, etc.

PSH
===

This is an app that is currently not used. It contains a models for storing a tree structure of
something which is called `Polythematic structured vocabulary` and which is used by some libraries
for categorization of their books. We might need it in the future, so we keep it there.

Source data
===========

This is again more of a stub that a fully developed app. It is intended to store data about
external sources of data that could be used to create candidates. The idea is to have something
similar to the ``Aleph`` app but for data outside of the catalogue. It should be used as a
transition between the external source and the ``Candidates`` app.

This is where we need to put some work in at the present to be able to read as much data as
possible from the ONIX format (see `Importers`_ above) and make it available inside the UI.
