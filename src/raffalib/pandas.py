# raffalib-python Miscellaneous functions
# Copyright (C) 2026 Raffaele Mancuso
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas
import logging
import pandas_flavor as pf

# See: https://pandas.pydata.org/pandas-docs/stable/development/extending.html#define-original-properties
class SubclassedDataFrame2(pandas.DataFrame):

    # normal properties
    _metadata = ["initial_df"]

    @property
    def _constructor(self):
        return SubclassedDataFrame2

@pf.register_dataframe_method
def startlog(self):
    obj = SubclassedDataFrame2(self)
    obj.initial_df = self
    return obj

@pf.register_dataframe_method
def midlog(self, msg=""):
    return self.endlog(msg).startlog()

@pf.register_dataframe_method
def endlog(self, msg=""):
    if(self.shape != self.initial_df.shape):
        nrow0, ncol0 = self.initial_df.shape
        nrow1, ncol1 = self.shape
        dr = nrow0 - nrow1
        dc = ncol0 - ncol1
        if dr > 0:
            msg += f"Removed {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) rows. "
        elif dr < 0:
            dr = abs(dr)
            msg += f"Added {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) rows. "
        if dc > 0:
            msg += f"Removed {dc:,d}/{ncol0:,d} ({dc/ncol0:.2%}) columns."
        elif dc < 0:
            dc = abs(dc)
            msg += f"Added {dc:,d}/{ncol0:,d} ({dc/ncol0:.2%}) columns."
    else:
        nchanged = (self != self.initial_df)
        # missings are different than themselves
        # if both values are missing, set changed to False
        nchanged[self.isna() & self.initial_df.isna()] = False
        # Get total number of cells that have changed
        nchanged = nchanged.sum().sum()
        if(nchanged == 0):
            msg += "No changes detected."
        else:
            ntot = self.initial_df.size
            msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged/ntot:.2%}) values"
    logging.getLogger("pandas-utils").info(msg)
    del self.initial_df
    return self

class SubclassedSeries(pandas.Series):

    # normal properties
    _metadata = ["initial_series"]

    @property
    def _constructor(self):
        return SubclassedSeries

@pf.register_series_method
def startlog(self):
    obj = SubclassedSeries(self)
    obj.initial_series = self
    return obj

@pf.register_series_method
def midlog(self, msg=""):
    return self.endlog(msg).startlog()

@pf.register_series_method
def endlog(self, msg=""):
    if(self.shape != self.initial_series.shape):
        nrow0 = self.initial_series.shape[0]
        nrow1 = self.shape[0]
        dr = nrow0 - nrow1
        if dr > 0:
            msg += f"Removed {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) values. "
        elif dr < 0:
            dr = abs(dr)
            msg += f"Added {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) values. "
    else:
        nchanged = (self != self.initial_series)
        # missings are different than themselves
        nchanged[self.isna() & self.initial_series.isna()] = False
        nchanged = nchanged.sum()
        if(nchanged == 0):
            msg += "No changes detected."
        else:
            ntot = self.initial_series.size
            msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged/ntot:.2%}) values."
    logging.getLogger("pandas-utils").info(msg)
    del self.initial_series
    return self

@pf.register_series_method
def value_counts_all(self, dropna=False):
    tempdf = pandas.DataFrame(self.value_counts(dropna=dropna, normalize=False))
    tempdf = tempdf.join(self.value_counts(dropna=dropna, normalize=True))
    totals_row = tempdf.agg({"count": ["sum"], "proportion": ["sum"]}).rename(
        index={"sum": "Total"}
    )
    return pandas.concat([tempdf, totals_row])

@pf.register_dataframe_method
def add_prefix_if_not_exists(df, prefix):
    """
    Add a prefix to all columns that do not already have it.
    """
    new_cols = {
        col: f"{prefix}{col}" for col in df.columns if not col.startswith(prefix)
    }
    return df.rename(columns=new_cols)