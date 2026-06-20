Quickstart
==========

This page gets you from zero to a logged data-wrangling pipeline in a couple of
minutes. For the full tour see :doc:`examples`.

Install
-------

Install the package together with the extras you need (see :doc:`installation`
for details):

.. code-block:: console

   uv add --editable "/path/to/raffalib-python[pandas,polars]"

Set up a logger
---------------

The change-logging accessors emit their messages through the standard
:mod:`logging` module. Call :func:`raffalib.create_logger` once to configure it:

.. code-block:: python

   import raffalib

   raffalib.create_logger(rich=False, fmt="{message}")

Use ``rich=True`` for colourised console output, or drop ``fmt`` to keep the
default ``timestamp - level - name - message`` format.

Log changes in a pipeline
-------------------------

Importing :mod:`raffalib.pandas` (or :mod:`raffalib.polars`) registers a
``.raffa`` accessor. Wrap any pipeline between ``startlog()`` and ``endlog()``
to log how the data changed:

.. code-block:: python

   import pandas as pd
   import raffalib.pandas  # registers the `.raffa` accessor

   df = pd.read_csv("penguins.csv")

   # Row/column count changes are logged automatically
   df = df.raffa.startlog().dropna(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
   # -> Removed 2/344 (0.58%) rows.

   # Pass clone=True to also detect value-level changes when the shape is unchanged
   df = df.raffa.startlog(clone=True).fillna(0).raffa.endlog(timeit=False)
   # -> Changed 19/2,752 (0.69%) values.

The polars accessor works identically:

.. code-block:: python

   import polars as pl
   import raffalib.polars  # registers the `.raffa` namespace

   df = pl.read_csv("penguins.csv")
   df = df.raffa.startlog().filter(pl.col("species") == "Adelie").raffa.endlog(timeit=False)
   # -> Removed 192/344 (55.81%) rows.

Next steps
----------

- :doc:`examples` — logging concepts, ``freq`` / ``crosstab``, logging joins,
  and Word export for both backends.
- **API Reference** (sidebar) — the full, docstring-generated reference.
