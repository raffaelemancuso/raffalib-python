# raffalib-python

A Python library of helper functions for data wrangling. Its main purpose is to
enrich [pandas](https://pandas.pydata.org/) and [polars](https://pola.rs/) with
[STATA](https://www.stata.com/)-like logging and `.docx` export capabilities, but
it also bundles assorted utilities for logging, pickling, progress bars, Selenium,
SQLAlchemy, and bibliometrics.

📖 **Documentation:** <https://raffalib-python.readthedocs.io> —
[Quickstart](https://raffalib-python.readthedocs.io/en/latest/quickstart.html) ·
[Examples](https://raffalib-python.readthedocs.io/en/latest/examples.html) ·
API Reference

> ⚠️ This project is under active development.

## Highlights

- **STATA-like logging** — wrap a pandas/polars pipeline in `startlog()` / `endlog()`
  and get a log line describing how many rows, columns, or cell values changed (and
  optionally how long it took).
- **`.docx` export** — write any DataFrame straight to a Word table with `to_docx()`.
- **Frequency & cross tables** — `freq()` and `crosstab()` accessors for quick
  tabulations.
- **Smarter joins** — a `join()` wrapper (pandas *and* polars) that logs where the
  output rows came from (left only / right only / both, dropped rows, duplicate keys),
  and auto-detects filtering (`semi`/`anti`) joins.

## Installation

Requires **Python ≥ 3.13**. The package is distributed as a local/editable install.

```console
# with uv
uv add --editable /path/to/raffalib-python

# or with pip
python3 -m pip install --editable /path/to/raffalib-python
```

### Optional dependencies

Core install is intentionally light. Heavier integrations live behind extras, so you
only pull in what you use:

| Extra            | Enables                                              |
| ---------------- | ---------------------------------------------------- |
| `pandas`         | `raffalib.pandas` accessors                          |
| `polars`         | `raffalib.polars` accessors and join logging         |
| `bibliometrics`  | OpenAlex / Scopus helpers                            |
| `crypto`         | KeePassXC / GnuPG helpers                            |
| `db`             | SQLAlchemy view helpers                              |
| `web`            | Selenium helpers                                     |
| `docs`           | Build the Sphinx documentation                       |
| `dev`            | Ruff + pytest for development                        |

```console
# example: install with the pandas and polars extras
uv add --editable "/path/to/raffalib-python[pandas,polars]"
```

## Quick start

### Logging changes in a pandas pipeline

```python
import pandas as pd
import raffalib
import raffalib.pandas  # registers the `.raffa` accessor

logger = raffalib.create_logger(rich=False, fmt="{message}")

df = pd.read_csv("penguins.csv")

# Shape changes are logged automatically
_ = df.raffa.startlog().dropna(subset=["bill_depth_mm"]).raffa.endlog(timeit=False)
# -> Removed 2/344 (0.58%) rows.

# Pass clone=True to also detect value-level changes when the shape is unchanged
_ = df.raffa.startlog(clone=True).fillna(0).raffa.endlog(timeit=False)
# -> Changed 19/2,752 (0.69%) values.
```

### The same with polars

```python
import polars as pl
import raffalib
import raffalib.polars  # registers the `.raffa` namespace

logger = raffalib.create_logger(rich=False, fmt="{message}")

df = pl.read_csv("penguins.csv")

_ = df.raffa.startlog().filter(pl.col("species") == "Adelie").raffa.endlog(timeit=False)
# -> Removed 192/344 (55.81%) rows.
```

Both backends share the same `startlog(clone=False)` / `endlog(custom_msg=None, timeit=True)`
signature. Set `timeit=True` (the default) to append an elapsed-time line.

### Logging joins (pandas & polars)

Both accessors expose the same `join()` wrapper — over `pd.DataFrame.merge` for
pandas and `pl.DataFrame.join` for polars — with identical logging output:

```python
out = df1.raffa.join(df2, on="A", how="left")
# Total rows in output table: 4
# From left only: 1/4 (25.00%)
# From right only: 0/4 (0.00%)
# From both: 3/4 (75.00%) (left dups 0, right dups 0)
# Dropped rows from left: 0/4 (0.00%)
# Dropped rows from right: 2/5 (40.00%)
```

Filtering joins (`how="semi"` / `how="anti"`) are detected automatically, and
`keep_row_index=True` keeps the source row-index columns in the output.

### Exporting to Word

```python
df.raffa.to_docx("table.docx")

# Heading and table options are routed to the right place automatically
df.raffa.to_docx("table.docx", heading_text="Table 1", table_style="Light Grid")
```

See the [Examples](https://raffalib-python.readthedocs.io) page for the full walkthrough.

## Modules

| Module                  | What it provides                                                        |
| ----------------------- | ---------------------------------------------------------------------- |
| `raffalib.pandas`       | `.raffa` accessor: `startlog`/`endlog`/`midlog`, `join`, `freq`, `to_docx`, `add_prefix_if_not_exists`, `get_duplicates`, `sort_columns` |
| `raffalib.polars`       | `.raffa` namespace: logging, `freq`, `crosstab`, `join`, `replace_string_with_null`, `to_docx` |
| `raffalib.logging`      | `create_logger` — opinionated logging setup (plain or `rich`)          |
| `raffalib.export_docx`  | `DocxFile` — low-level Word document/table builder                     |
| `raffalib.tqdm`         | `tqdm_batch` — batched progress bars                                    |
| `raffalib.itertools`    | `batch_boundaries` — compute batch start/end indices                   |
| `raffalib.list_replace` | `list_replace` — replace occurrences in a list                         |
| `raffalib.mypickle`     | `read_pickle` / `write_pickle` helpers                                  |
| `raffalib.selenium`     | Scrolling and explicit-wait helpers for Selenium WebDriver             |
| `raffalib.sqlalchemy`   | SQLAlchemy `CREATE VIEW` / `DROP VIEW` constructs and a `view()` helper |
| `raffalib.ScopusUtils`  | Scopus API helpers                                                      |
| `raffalib.check_openalex_api_key` | Validate an OpenAlex API key                                 |

## Development

```console
uv sync --extra dev
uv run pytest        # run the test suite
uv run ruff check    # lint
uv run ruff format   # format
```

## License

Released under the [GNU General Public License v3.0 or later](LICENSE.txt).

Copyright © 2026 Raffaele Mancuso.
