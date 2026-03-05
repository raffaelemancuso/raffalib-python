# raffalib-python

## Introduction

A library with helper functions for pandas, polars, selenium, and others

The main purpose of this library is to obtain STATA-like logs with pandas and polars.

But other data analysis functions are available as well.

## Installation

1. Clone the repository
2. In the folder of your project, add the requirement:

    ```
    uv add --editable [PATH_TO_LOCAL_REPO]
    ```
 
    or, if you are not using `uv`,:

    ```
    python3 -m pip install --editable [PATH_TO_LOCAL_REPO]
    ```

# Examples
 
## Pandas logging

Try to run the following example.

```python
import pandas as pd
import raffalib
import raffalib.pandas

logger = raffalib.create_logger()
df = pd.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/refs/heads/main/inst/extdata/penguins.csv")
df.head()
logger.info("Drop rows with missing bill_depth_mm")
_ = df.raffa.startlog().dropna(subset=["bill_depth_mm"]).raffa.endlog()
logger.info("Drop non Adelie penguins")
_ = df.raffa.startlog().query("species=='Adelie'").raffa.endlog()
logger.info("Drop columns")
_ = df.raffa.startlog().drop(["bill_length_mm", "bill_depth_mm"], axis=1).raffa.endlog()
logger.info("Fill missings (trial 1)")
_ = df.raffa.startlog().fillna(0).raffa.endlog()
logger.info("Fill missings (trial 2)")
_ = df.raffa.startlog(clone=True).fillna(0).raffa.endlog()
```

This will result in:

```
2026-02-25 15:23:03 INFO     root: Drop rows with missing bill_depth_mm                               <python-input-1>:9
                    INFO     raffalib.pandas: Removed 2/344 (0.58%) rows.                                   pandas.py:78
                    INFO     root: Drop non Adelie penguins                                          <python-input-1>:11
                    INFO     raffalib.pandas: Removed 192/344 (55.81%) rows.                                pandas.py:78
                    INFO     root: Drop columns                                                      <python-input-1>:13
                    INFO     raffalib.pandas: Removed 2/8 (25.00%) columns.                                 pandas.py:78
                    INFO     root: Fill missings (trial 1)                                           <python-input-1>:15
                    INFO     raffalib.pandas: Shape is the same and DataFrame was not cloned                pandas.py:78
                    INFO     root: Fill missings (trial 2)                                           <python-input-1>:17
                    INFO     raffalib.pandas: Changed 19/2,752 (0.69%) values                               pandas.py:78
```

Frequency tables with proportions are available (sorted in descending order per proportion):

```
>>> df.raffa.freq("species")
           count  proportion
Adelie       152    0.441860
Gentoo       124    0.360465
Chinstrap     68    0.197674
Total        344    1.000000
```