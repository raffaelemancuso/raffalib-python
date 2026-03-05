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

"""
Example of usage

>>> import pandas as pd
>>> import raffalib
>>> import raffalib.pandas
>>> 
>>> logger = raffalib.create_logger(rich=False, fmt="{message}")
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
Changed 19/2,752 (0.69%) values
"""

import pandas as pd
import logging
from natsort import natsorted

logger = logging.getLogger(__name__)

@pd.api.extensions.register_series_accessor("raffa")
class RaffaSeries:

    def __init__(self, data):
        self._series = data
        self._series._metadata += ["_initial_shape", "_initial_df"]

    def startlog(self, clone=False):
        self._series._initial_shape = self._series.shape
        if clone:
            self._series._initial_series = self._data.copy()
        else:
            self._series._initial_series = None
        return self._series

    def midlog(self, msg=""):
        return self.endlog(msg).startlog()

    def endlog(self, msg=""):
        initial_shape = self._series._initial_shape
        final_shape = self._series.shape
        if(final_shape != initial_shape):
            nrow0 = initial_shape[0]
            nrow1 = final_shape[0]
            dr = nrow0 - nrow1
            if dr > 0:
                msg += f"Removed {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) values. "
            elif dr < 0:
                dr = abs(dr)
                msg += f"Added {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) values. "
        else:
            if(self._series._initial_series):
                nchanged = (self._series != self._series._initial_series)
                # missings are different than themselves
                nchanged[self._series.isna() & self._series._initial_series.isna()] = False
                nchanged = nchanged.sum()
                if(nchanged == 0):
                    msg += "No changes detected."
                else:
                    ntot = self._series._initial_series.size
                    msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged/ntot:.2%}) values."
            else:
                msg = "Shape is the same. No value-level comparison done because clone=False was used in startlog()."
        logger.info(msg)
        del self._series._initial_series
        del self._series._initial_shape
        return self._series

    def freq(self, dropna=False):
        tempdf = pd.DataFrame(self._series.value_counts(dropna=dropna, normalize=False))
        tempdf = tempdf.join(self._series.value_counts(dropna=dropna, normalize=True))
        totals_row = tempdf.agg({"count": ["sum"], "proportion": ["sum"]}).rename(
            index={"sum": "Total"}
        )
        df = pd.concat([tempdf, totals_row])
        df.index.name = self._series.name
        return df

# See: https://pandas.pydata.org/pandas-docs/stable/development/extending.html#registering-custom-accessors
@pd.api.extensions.register_dataframe_accessor("raffa")
class RaffaDataFrame:
    
    def __init__(self, data):
        self._df = data
        self._df._metadata += ["_initial_shape", "_initial_df"]

    def startlog(self, clone=False):
        self._df._initial_shape = self._df.shape
        if clone:
            self._df._initial_df = self._df.copy()
        else:
            self._df._initial_df = None
        return self._df

    def midlog(self, msg=""):
        return self.endlog(msg).startlog()

    def endlog(self, msg=""):
        final_shape = self._df.shape
        initial_shape = self._df._initial_shape
        if(final_shape != initial_shape):
            nrow0, ncol0 = initial_shape
            nrow1, ncol1 = final_shape
            dr = nrow0 - nrow1
            dc = ncol0 - ncol1
            if dr > 0:
                msg += f"Removed {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) rows."
            elif dr < 0:
                dr = abs(dr)
                msg += f"Added {dr:,d}/{nrow0:,d} ({dr/nrow0:.2%}) rows."
            if dc > 0:
                msg += f"Removed {dc:,d}/{ncol0:,d} ({dc/ncol0:.2%}) columns."
            elif dc < 0:
                dc = abs(dc)
                msg += f"Added {dc:,d}/{ncol0:,d} ({dc/ncol0:.2%}) columns."
        else:
            initial_df = self._df._initial_df
            if(initial_df is not None):
                nchanged = (self._df != initial_df)
                # missings are different than themselves
                # if both values are missing, set changed to False
                nchanged[self._df.isna() & initial_df.isna()] = False
                # Get total number of cells that have changed
                nchanged = nchanged.sum().sum()
                if(nchanged == 0):
                    msg += "No changes detected."
                else:
                    ntot = initial_df.size
                    msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged/ntot:.2%}) values"
            else:
                msg = "Shape is the same. No value-level comparison done because clone=False was used in startlog()."
        logger.info(msg)
        del self._df._initial_df
        del self._df._initial_shape
        return self._df
        
    def add_prefix_if_not_exists(df, prefix):
        """
        Add a prefix to all columns that do not already have it.
        """
        new_cols = {
            col: f"{prefix}{col}" for col in df._df.columns if not col.startswith(prefix)
        }
        return df._df.rename(columns=new_cols)
        
    def get_duplicates(self, *args, **kwargs):
        mask = self._df.duplicated(*args, **kwargs)
        return self._df[mask]
        
    def move_columns(self, start=[], end=[]):
        for x in start+end:
            assert x in self._df.columns
        cols = [x for x in self._df.columns if ((x not in start) and (x not in end))]
        self._df = self._df[start + cols + end]
        return self._df
    
    def sort_columns(self):
        self._df = self._df[natsorted(self._df.columns)]
        return self._df
        
    def freq(self, colname):
        return self._df[colname].raffa.freq()

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_NDIFF)