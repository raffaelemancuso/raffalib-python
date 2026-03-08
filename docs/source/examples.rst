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

Example of usage

>>> import polars as pl
>>> import polars.selectors as cs
>>> import raffalib
>>> import raffalib.polars
>>> 
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")
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
>>> _ = df.raffa.startlog().drop_nulls(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
Removed 2/344 (0.58%) rows.
>>> _ = df.raffa.startlog().filter(pl.col("species")=="Adelie").raffa.endlog(timeit=False)
Removed 192/344 (55.81%) rows.
>>> _ = df.raffa.startlog().select(pl.exclude(["bill_length_mm", "bill_depth_mm"])).raffa.endlog(timeit=False)
Removed 2/8 (25.00%) columns.
>>> _ = df.raffa.startlog().fill_null(0).raffa.endlog(timeit=False)
Shape is the same. No value-level comparison done because clone=False was used in startlog().
>>> _ = df.raffa.startlog(clone=True).fill_null("0").raffa.endlog(timeit=False)
Changed 11/2,752 (0.40%) values.