########
Examples
########

This guide walks through the main features of **raffalib-python**. For a faster
introduction see :doc:`quickstart`.

****************
Logging concepts
****************

Importing :mod:`raffalib.pandas` or :mod:`raffalib.polars` registers a ``.raffa``
accessor (a namespace on polars, an accessor on pandas) that adds STATA-like
change logging to a Series or DataFrame.

The pattern is always the same: call ``startlog()`` before an operation and
``endlog()`` after it. ``endlog`` logs how the data changed — rows or columns
added/removed or, when the shape is unchanged, how many cell values changed.

``startlog(clone=False)``
   Snapshots the current shape (and a timestamp). Pass ``clone=True`` to also
   keep a copy of the data, so that **value-level** changes can be detected when
   the shape does not change. This costs extra memory.

``endlog(custom_msg=None, timeit=True)``
   Logs the change. ``custom_msg`` is prepended to the message; ``timeit=True``
   appends the elapsed time since ``startlog``. The signature is identical for
   pandas and polars.

``midlog(custom_msg=None, timeit=True)`` *(pandas only)*
   A convenience alias for ``endlog().startlog()`` — log the current step and
   immediately start the next one.

Messages are emitted through the standard :mod:`logging` module; configure it
once with :func:`raffalib.create_logger` (see :ref:`utilities`). The examples
below pass ``timeit=False`` so the output is deterministic; in real use you will
usually keep the default ``timeit=True``.

******
pandas
******

Logging
=======

>>> import pandas as pd
>>> import raffalib
>>> import raffalib.pandas
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")
>>>
>>> df = pd.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/refs/heads/main/inst/extdata/penguins.csv")
>>> df.head()
  species     island  bill_length_mm  bill_depth_mm  flipper_length_mm  body_mass_g     sex  year
0  Adelie  Torgersen            39.1           18.7              181.0       3750.0    male  2007
1  Adelie  Torgersen            39.5           17.4              186.0       3800.0  female  2007
2  Adelie  Torgersen            40.3           18.0              195.0       3250.0  female  2007
3  Adelie  Torgersen             NaN            NaN                NaN          NaN     NaN  2007
4  Adelie  Torgersen            36.7           19.3              193.0       3450.0  female  2007

Removing rows, filtering, or dropping columns changes the shape, which is
logged automatically:

>>> _ = df.raffa.startlog().dropna(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
Removed 2/344 (0.58%) rows.
>>> _ = df.raffa.startlog().query("species=='Adelie'").raffa.endlog(timeit=False)
Removed 192/344 (55.81%) rows.
>>> _ = df.raffa.startlog().drop(["bill_length_mm", "bill_depth_mm"], axis=1).raffa.endlog(timeit=False)
Removed 2/8 (25.00%) columns.

Operations that change values but not the shape need ``clone=True`` so the
initial data can be compared against:

>>> _ = df.raffa.startlog().fillna(0).raffa.endlog(timeit=False)
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = df.raffa.startlog(clone=True).fillna(0).raffa.endlog(timeit=False)
Changed 19/2,752 (0.69%) values.

The same accessor is available on a Series:

>>> s = df["bill_length_mm"]
>>> _ = s.raffa.startlog().dropna().raffa.endlog(timeit=False)
Removed 2/344 (0.58%) values.
>>> _ = s.raffa.startlog(clone=True).fillna(0).raffa.endlog(timeit=False)
Changed 2/344 (0.58%) values.

Frequency tables
================

``freq`` builds a frequency table with counts, proportions, and a ``Total`` row:

>>> s = pd.Series(["a", "a", "b", "c", "a"], name="letter")
>>> s.raffa.freq()
        count  proportion
letter
a           3         0.6
b           1         0.2
c           1         0.2
Total       5         1.0

On a DataFrame, pass the column name (it delegates to the Series accessor):

>>> df.raffa.freq("species")

Joins
=====

The ``join`` accessor wraps :meth:`pandas.DataFrame.merge` and logs where the
output rows come from. It mirrors the polars ``join`` accessor described below.

>>> df1 = pd.DataFrame({"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]})
>>> df2 = pd.DataFrame({"A": ["a1", "a2", "a3", "a5", "a6"], "C": ["c1", "c2", "c3", "c5", "c6"]})

Mutating joins
--------------

Outer join:

>>> _ = df1.raffa.join(df2, on="A", how="outer")
Total rows in output table: 6
From left only: 1/6 (16.67%)
From right only: 2/6 (33.33%)
From both: 3/6 (50.00%) (left dups 0, right dups 0)
Dropped rows from left: 0/4 (0.00%)
Dropped rows from right: 0/5 (0.00%)

Inner join:

>>> _ = df1.raffa.join(df2, on="A", how="inner")
Total rows in output table: 3
From left only: 0/3 (0.00%)
From right only: 0/3 (0.00%)
From both: 3/3 (100.00%) (left dups 0, right dups 0)
Dropped rows from left: 1/4 (25.00%)
Dropped rows from right: 2/5 (40.00%)

Left join:

>>> _ = df1.raffa.join(df2, on="A", how="left")
Total rows in output table: 4
From left only: 1/4 (25.00%)
From right only: 0/4 (0.00%)
From both: 3/4 (75.00%) (left dups 0, right dups 0)
Dropped rows from left: 0/4 (0.00%)
Dropped rows from right: 2/5 (40.00%)

Right join:

>>> _ = df1.raffa.join(df2, on="A", how="right")
Total rows in output table: 5
From left only: 0/5 (0.00%)
From right only: 2/5 (40.00%)
From both: 3/5 (60.00%) (left dups 0, right dups 0)
Dropped rows from left: 1/4 (25.00%)
Dropped rows from right: 0/5 (0.00%)

Filtering joins
---------------

``how="semi"`` and ``how="anti"`` are not native to pandas; the accessor
emulates them and detects them as filtering joins:

>>> _ = df1.raffa.join(df2, on="A", how="semi", keep_row_index=False)
Detected filtering join. Rows variation -1/4 (-25.00%), total rows after join: 3/4 (75.00%)
>>> _ = df1.raffa.join(df2, on="A", how="anti", keep_row_index=False)
Detected filtering join. Rows variation -3/4 (-75.00%), total rows after join: 1/4 (25.00%)

Pass ``keep_row_index=True`` on a mutating join to keep the ``source_left`` /
``source_right`` row-index columns in the output.

Word export
===========

Export a DataFrame to a Word ``.docx`` table:

>>> df.head(5).raffa.to_docx("table.docx")

Keyword arguments are forwarded to :class:`~raffalib.export_docx.DocxFile` —
document and heading options (e.g. ``heading_text``, ``landscape``) — or to its
``add_table`` method — table options (e.g. ``table_style``, ``table_font_size``):

>>> df.head(5).raffa.to_docx("table.docx", heading_text="Table 1", table_style="Light Grid")

******
polars
******

Logging
=======

Let's import the libraries and create a logger:

>>> import polars as pl
>>> import polars.selectors as cs
>>> import raffalib
>>> import raffalib.polars
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")

Let's load a dataset. ``replace_string_with_null`` turns the literal ``"NA"``
strings used by this CSV into proper nulls:

>>> df = pl.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/refs/heads/main/inst/extdata/penguins.csv")
>>> df = df.raffa.replace_string_with_null("NA")
>>> df = df.with_columns(pl.col(["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]).cast(pl.Float32).name.keep())
>>> df.head()
shape: (5, 8)
┌─────────┬───────────┬────────────────┬───────────────┬───────────────────┬─────────────┬────────┬───────┐
│ species ┆ island    ┆ bill_length_mm ┆ bill_depth_mm ┆ flipper_length_mm ┆ body_mass_g ┆ sex    ┆ year  │
│ ---     ┆ ---       ┆ ---            ┆ ---           ┆ ---               ┆ ---         ┆ ---    ┆ ---   │
│ str     ┆ str       ┆ f32            ┆ f32           ┆ f32               ┆ f32         ┆ str    ┆ i64   │
╞═════════╪═══════════╪════════════════╪═══════════════╪═══════════════════╪═════════════╪════════╪═══════╡
│ Adelie  ┆ Torgersen ┆ 39.099998      ┆ 18.700001     ┆ 181.0             ┆ 3,750.0     ┆ male   ┆ 2,007 │
│ Adelie  ┆ Torgersen ┆ 39.5           ┆ 17.4          ┆ 186.0             ┆ 3,800.0     ┆ female ┆ 2,007 │
│ Adelie  ┆ Torgersen ┆ 40.299999      ┆ 18.0          ┆ 195.0             ┆ 3,250.0     ┆ female ┆ 2,007 │
│ Adelie  ┆ Torgersen ┆ null           ┆ null          ┆ null              ┆ null        ┆ null   ┆ 2,007 │
│ Adelie  ┆ Torgersen ┆ 36.700001      ┆ 19.299999     ┆ 193.0             ┆ 3,450.0     ┆ female ┆ 2,007 │
└─────────┴───────────┴────────────────┴───────────────┴───────────────────┴─────────────┴────────┴───────┘

Removing rows with nulls, filtering values, or selecting columns changes the
shape, which is logged:

>>> _ = df.raffa.startlog().drop_nulls(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
Removed 2/344 (0.58%) rows.
>>> _ = df.raffa.startlog().filter(pl.col("species")=="Adelie").raffa.endlog(timeit=False)
Removed 192/344 (55.81%) rows.
>>> _ = df.raffa.startlog().select(pl.exclude(["bill_length_mm", "bill_depth_mm"])).raffa.endlog(timeit=False)
Removed 2/8 (25.00%) columns.

Operations that change values but not the shape need ``clone=True``:

>>> _ = df.raffa.startlog().fill_null(0).raffa.endlog(timeit=False)
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = df.raffa.startlog(clone=True).fill_null("0").raffa.endlog(timeit=False)
Changed 11/2,752 (0.40%) values.

Frequency and cross tables
==========================

``freq`` builds a frequency table for a column, with counts, percentages, and a
``Total`` row:

>>> sp = pl.Series("letter", ["a", "a", "b", "c", "a"])
>>> sp.raffa.freq()
shape: (4, 3)
┌───────┬───────┬───────┐
│ value ┆ count ┆ perc  │
│ ---   ┆ ---   ┆ ---   │
│ str   ┆ u32   ┆ f64   │
╞═══════╪═══════╪═══════╡
│ a     ┆ 3     ┆ 60.0  │
│ b     ┆ 1     ┆ 20.0  │
│ c     ┆ 1     ┆ 20.0  │
│ Total ┆ 5     ┆ 100.0 │
└───────┴───────┴───────┘

On a DataFrame, pass the column name (equivalent to
``df.get_column("species").raffa.freq()``):

>>> df.raffa.freq("species")

``crosstab`` builds a contingency table of two columns:

>>> ct = pl.DataFrame({"grp": ["x", "x", "y", "y", "y"], "cls": ["m", "n", "m", "m", "n"]})
>>> ct.raffa.crosstab("grp", "cls")
shape: (2, 3)
┌─────┬─────┬─────┐
│ grp ┆ m   ┆ n   │
│ --- ┆ --- ┆ --- │
│ str ┆ u32 ┆ u32 │
╞═════╪═════╪═════╡
│ x   ┆ 1   ┆ 1   │
│ y   ┆ 2   ┆ 1   │
└─────┴─────┴─────┘

Use ``perc`` to express each cell as a percentage along an axis (see
:class:`~raffalib.polars.PercOptions`):

>>> from raffalib.polars import PercOptions
>>> ct.raffa.crosstab("grp", "cls", perc=PercOptions.ROWS)
shape: (2, 3)
┌─────┬───────────┬───────────┐
│ grp ┆ m         ┆ n         │
│ --- ┆ ---       ┆ ---       │
│ str ┆ f64       ┆ f64       │
╞═════╪═══════════╪═══════════╡
│ x   ┆ 50.0      ┆ 50.0      │
│ y   ┆ 66.666667 ┆ 33.333333 │
└─────┴───────────┴───────────┘

Joins
=====

The ``join`` accessor wraps :meth:`polars.DataFrame.join` and logs the row
provenance of the result.

>>> df1 = pl.DataFrame({"A": ["a1", "a2", "a3", "a4"], "B": ["b1", "b2", "b3", "b4"]})
>>> df2 = pl.DataFrame({"A": ["a1", "a2", "a3", "a5", "a6"], "C": ["c1", "c2", "c3", "c5", "c6"]})

Mutating joins
--------------

Outer join:

>>> _ = df1.raffa.join(df2, on="A", how="outer")
Total rows in output table: 6
From left only: 1/6 (16.67%)
From right only: 2/6 (33.33%)
From both: 3/6 (50.00%) (left dups 0, right dups 0)
Dropped rows from left: 0/4 (0.00%)
Dropped rows from right: 0/5 (0.00%)

Inner join:

>>> _ = df1.raffa.join(df2, on="A", how="inner")
Total rows in output table: 3
From left only: 0/3 (0.00%)
From right only: 0/3 (0.00%)
From both: 3/3 (100.00%) (left dups 0, right dups 0)
Dropped rows from left: 1/4 (25.00%)
Dropped rows from right: 2/5 (40.00%)

Left join:

>>> _ = df1.raffa.join(df2, on="A", how="left")
Total rows in output table: 4
From left only: 1/4 (25.00%)
From right only: 0/4 (0.00%)
From both: 3/4 (75.00%) (left dups 0, right dups 0)
Dropped rows from left: 0/4 (0.00%)
Dropped rows from right: 2/5 (40.00%)

Right join:

>>> _ = df1.raffa.join(df2, on="A", how="right")
Total rows in output table: 5
From left only: 0/5 (0.00%)
From right only: 2/5 (40.00%)
From both: 3/5 (60.00%) (left dups 0, right dups 0)
Dropped rows from left: 1/4 (25.00%)
Dropped rows from right: 0/5 (0.00%)

Filtering joins
---------------

Filtering joins (``how="semi"`` / ``how="anti"``) are automatically detected:

>>> _ = df1.raffa.join(df2, on="A", how="semi", keep_row_index=False)
Detected filtering join. Rows variation -1/4 (-25.00%), total rows after join: 3/4 (75.00%)
>>> _ = df1.raffa.join(df2, on="A", how="anti", keep_row_index=False)
Detected filtering join. Rows variation -3/4 (-75.00%), total rows after join: 1/4 (25.00%)

Word export
===========

Export a DataFrame to a Word ``.docx`` file:

>>> df = pl.DataFrame({"a": [1, 2, 3], "b": ["AAA", "BBB", "CCC"]})
>>> df.raffa.to_docx("main.docx")

As with pandas, document/heading and table options can be passed as keyword
arguments and are routed to the right place:

>>> df.raffa.to_docx("main.docx", heading_text="Table 1", landscape=True)

.. _utilities:

*********
Utilities
*********

Beyond the DataFrame accessors, ``raffalib`` ships a handful of standalone
helpers.

Logger setup
============

:func:`raffalib.create_logger` configures the standard-library logger used by
the change-logging accessors:

>>> import raffalib
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")

Pass ``rich=True`` for colourised console output via
`rich <https://rich.readthedocs.io/>`_, or omit ``fmt`` for the default
``timestamp - level - name - message`` layout.

Batched iteration
=================

:func:`raffalib.tqdm_batch` wraps a sized iterable in a
`tqdm <https://tqdm.github.io/>`_ progress bar that advances once per batch:

>>> from raffalib import tqdm_batch
>>> for batch in tqdm_batch(items, batch_size=100)():
...     process(batch)

:func:`raffalib.itertools.batch_boundaries` is the index-only equivalent,
yielding ``(batch_index, start, end)`` tuples (1-based, inclusive):

>>> from raffalib.itertools import batch_boundaries
>>> list(batch_boundaries(20, 3))
[(0, 1, 3), (1, 4, 6), (2, 7, 9), (3, 10, 12), (4, 13, 15), (5, 16, 18), (6, 19, 20)]

List editing
============

:func:`raffalib.list_replace` replaces every occurrence of a value in a list,
in place:

>>> from raffalib import list_replace
>>> lst = [1, 2, 3, 2, 4]
>>> list_replace(lst, 2, 5)
>>> lst
[1, 5, 3, 5, 4]

Pickling
========

:func:`raffalib.mypickle.write_pickle` and :func:`raffalib.mypickle.read_pickle`
serialise arbitrary Python objects with
`jsonpickle <https://jsonpickle.github.io/>`_, writing to a timestamped file
named ``{stem}_{YYYY-MM-DD-HH-MM-SS}``:

>>> from pathlib import Path
>>> from raffalib.mypickle import write_pickle, read_pickle
>>> write_pickle({"a": 1}, Path("."), "mydata")
>>> obj = read_pickle(Path("mydata_2026-06-20-09-30-00"))
