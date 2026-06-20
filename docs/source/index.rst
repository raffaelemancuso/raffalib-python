.. raffalib-python documentation master file, created by
   sphinx-quickstart on Mon Feb 16 10:41:01 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

raffalib-python documentation
=============================

**raffalib-python** is a small library of helper functions for data wrangling.

Its main purpose is to enrich `pandas <https://pandas.pydata.org/>`_ and
`polars <https://pola.rs/>`_ with `STATA <https://www.stata.com/>`_-like logging
and ``.docx`` export capabilities, but it also bundles assorted utilities for
logging, pickling, progress bars, Selenium, SQLAlchemy, and bibliometrics.

Highlights
----------

- **STATA-like logging** — wrap a pandas/polars pipeline in ``startlog()`` /
  ``endlog()`` and get a log line describing how many rows, columns, or cell
  values changed (and optionally how long it took).
- **Logging joins** — a ``join()`` wrapper (for both backends) that logs where
  the output rows came from: left only, right only, both, dropped rows, and
  duplicate keys.
- **Frequency & cross tables** — ``freq()`` and ``crosstab()`` accessors for
  quick tabulations.
- **Word export** — write any DataFrame straight to a ``.docx`` table with
  ``to_docx()``.

A taste
-------

.. code-block:: python

   import pandas as pd
   import raffalib
   import raffalib.pandas  # registers the `.raffa` accessor

   raffalib.create_logger(rich=False, fmt="{message}")

   df = pd.read_csv("penguins.csv")
   df = df.raffa.startlog().dropna().raffa.endlog(timeit=False)
   # -> Removed 11/344 (3.20%) rows.

New here? Start with :doc:`quickstart`, then browse the :doc:`examples` for the
full tour. The complete API reference is generated from the source docstrings
under **API Reference** in the sidebar.

.. note::

   This project is under active development.

.. toctree::
   :hidden:

   Home page <self>
   Install <installation>
   Quickstart <quickstart>
   Examples <examples>
