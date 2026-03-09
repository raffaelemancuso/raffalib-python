Examples
========

pandas
------

DataFrame example:

>>> import pandas as pd
>>> from pathlib import Path
>>> import raffalib
>>> import raffalib.pandas
>>> from raffalib.export_docx import DocxOptions
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
>>> _ = df.raffa.startlog().dropna(subset=["bill_depth_mm"]).raffa.endlog()
Removed 2/344 (0.58%) rows.
>>> _ = df.raffa.startlog().query("species=='Adelie'").raffa.endlog()
Removed 192/344 (55.81%) rows.
>>> _ = df.raffa.startlog().drop(["bill_length_mm", "bill_depth_mm"], axis=1).raffa.endlog()
Removed 2/8 (25.00%) columns.
>>> _ = df.raffa.startlog().fillna(0).raffa.endlog()
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = df.raffa.startlog(clone=True).fillna(0).raffa.endlog()
Changed 19/2,752 (0.69%) values.
>>> outfp = Path("test.docx")
>>> outfp.unlink(missing_ok=True)
>>> docx_options = DocxOptions(heading_text = "Table 1")
>>> df.head(5).raffa.to_docx(outfp, docx_options=docx_options)
>>> assert outfp.is_file()
>>> outfp.unlink()

Series examples:

>>> s = df["bill_length_mm"]
>>> assert type(s)==pd.Series, type(s)
>>> _ = s.raffa.startlog().dropna().raffa.endlog()
Removed 2/344 (0.58%) values.
>>> _ = s.raffa.startlog().fillna(0).raffa.endlog()
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = s.raffa.startlog(clone=True).fillna(0).raffa.endlog()
Changed 2/344 (0.58%) values.

polars
------

Let' import the libraries and create a logger:

>>> import polars as pl
>>> import polars.selectors as cs
>>> import raffalib
>>> import raffalib.polars
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")

Let's load a dataset

>>> df = pl.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/refs/heads/main/inst/extdata/penguins.csv")
>>> df = df.raffa.startlog(clone=True).raffa.replace_string_with_null("NA").raffa.endlog(timeit=False)
Changed 19/2,752 (0.69%) values.
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

Let's see some data wrangling on this data: remove rows with null values, filtering certain values, or selecting certain columns:

>>> _ = df.raffa.startlog().drop_nulls(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
Removed 2/344 (0.58%) rows.
>>> _ = df.raffa.startlog().filter(pl.col("species")=="Adelie").raffa.endlog(timeit=False)
Removed 192/344 (55.81%) rows.
>>> _ = df.raffa.startlog().select(pl.exclude(["bill_length_mm", "bill_depth_mm"])).raffa.endlog(timeit=False)
Removed 2/8 (25.00%) columns.

Operations that do not change the shape of the DataFrame but only its values requires `clone=True`
in the `startlog` call to clone the entire initial dataframe for further comparison:

>>> _ = df.raffa.startlog().fill_null(0).raffa.endlog(timeit=False)
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = df.raffa.startlog(clone=True).fill_null("0").raffa.endlog(timeit=False)
Changed 11/2,752 (0.40%) values.

Let's see an example with joins:

>>> df1 = pl.DataFrame({"left_a": ["A", "B", "B", "C", "D"], "left_b": ["a", "b1", "b2", "c", "d"]})
>>> df2 = pl.DataFrame({"right_a": ["A", "A", "A", "B", "E"], "right_d": ["alpha1", "alpha2", "alpha3", "beta", "gamma"]})
>>> _ = df1.raffa.join(df2, left_on="left_a", right_on="right_a", how="full", keep_row_index=False)
Total rows in output table: 8
From left only: 2/8 (25.00%)
From right only: 1/8 (12.50%)
From both: 5/8 (62.50%) (left dups 3, right dups 2)
>>> _ = df1.raffa.join(df2, left_on="left_a", right_on="right_a", how="left", keep_row_index=False)
Total rows in output table: 7
From left only: 2/7 (28.57%)
From right only: 0/7 (0.00%)
From both: 5/7 (71.43%) (left dups 3, right dups 2)

Filtering joins are automatically detected:

>>> _ = df1.raffa.join(df2, left_on="left_a", right_on="right_a", how="semi", keep_row_index=False)
Detected filtering join. Rows variation -2/5 (-40.00%), total rows after join: 3/5 (60.00%)
>>> _ = df1.raffa.join(df2, left_on="left_a", right_on="right_a", how="anti", keep_row_index=False)
Detected filtering join. Rows variation -3/5 (-60.00%), total rows after join: 2/5 (40.00%)