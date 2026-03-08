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
Extensions for pandas
"""

import pandas as pd
import logging
from natsort import natsorted
from pathlib import Path
from .export_docx import prepare_docx, set_autofit, DocxOptions

logger = logging.getLogger(__name__)

# --- SERIES --- #

try:
    # delete the accessor to avoid warning
    # See: https://stackoverflow.com/questions/69720999/how-to-prevent-pandas-accessor-to-issue-override-warning
    del pd.Series.raffa
except AttributeError:
    pass


@pd.api.extensions.register_series_accessor("raffa")
class RaffaSeries:
    def __init__(self, data):
        self._series = data
        self._series._metadata += ["_initial_shape", "_initial_series"]

    def startlog(self, clone=False):
        """
        Initialize the logger.

        :param clone: Whether to clone the series. Takes more RAM but allows logging of changed values. Otherwise, only changed shapes is logged.
        :type clone: bool
        :return: The pandas Series for piping.
        :rtype: pd.Series
        """
        self._series._initial_shape = self._series.shape
        if clone:
            self._series._initial_series = self._series.copy()
        else:
            self._series._initial_series = None
        return self._series

    def midlog(self, msg=""):
        """
        Alias for `.endlog().startlog()`
        """
        return self.endlog(msg).startlog()

    def endlog(self, msg=""):
        """
        Log changes to the Series.

        :param msg: A custom message
        :type msg: str
        :return: The pandas Series for piping.
        :rtype: pd.Series
        """
        initial_shape = self._series._initial_shape
        final_shape = self._series.shape
        if final_shape != initial_shape:
            nrow0 = initial_shape[0]
            nrow1 = final_shape[0]
            dr = nrow0 - nrow1
            if dr > 0:
                msg += f"Removed {dr:,d}/{nrow0:,d} ({dr / nrow0:.2%}) values."
            elif dr < 0:
                dr = abs(dr)
                msg += f"Added {dr:,d}/{nrow0:,d} ({dr / nrow0:.2%}) values."
        else:
            if self._series._initial_series is not None:
                nchanged = self._series != self._series._initial_series
                # missings are different than themselves
                nchanged[self._series.isna() & self._series._initial_series.isna()] = (
                    False
                )
                nchanged = nchanged.sum()
                if nchanged == 0:
                    msg += "No changes detected."
                else:
                    ntot = self._series._initial_series.size
                    msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged / ntot:.2%}) values."
            else:
                msg += "Shape is the same. No value-level comparison done because clone=False was used in startlog()."
        logger.info(msg)
        del self._series._initial_series
        del self._series._initial_shape
        return self._series

    def freq(self, dropna:bool=False) -> pd.DataFrame:
        """
        Generate frequency table for this series
        
        :param dropna: Whether to drop missing values before generating frequency table
        :type dropna: bool
        :return: A DataFrame with frequency table
        :rtype: pd.DataFrame
        """
        tempdf = pd.DataFrame(self._series.value_counts(dropna=dropna, normalize=False))
        tempdf = tempdf.join(self._series.value_counts(dropna=dropna, normalize=True))
        totals_row = tempdf.agg({"count": ["sum"], "proportion": ["sum"]}).rename(
            index={"sum": "Total"}
        )
        df = pd.concat([tempdf, totals_row])
        df.index.name = self._series.name
        return df


# --- DATAFRAME --- #
try:
    # delete the accessor to avoid warning
    # See: https://stackoverflow.com/questions/69720999/how-to-prevent-pandas-accessor-to-issue-override-warning
    del pd.DataFrame.raffa
except AttributeError:
    pass


# See: https://pandas.pydata.org/pandas-docs/stable/development/extending.html#registering-custom-accessors
@pd.api.extensions.register_dataframe_accessor("raffa")
class RaffaDataFrame:
    def __init__(self, data: pd.DataFrame) -> None:
        self._df = data
        # See https://pandas.pydata.org/pandas-docs/stable/development/extending.html#define-original-properties
        self._df._metadata += ["_initial_shape", "_initial_df"]

    def startlog(self, clone: bool = False) -> pd.DataFrame:
        """
        Initialize the logger.

        :param clone: Whether to clone the series. Takes more RAM but allows logging of changed values. Otherwise, only changed shapes is logged.
        :type clone: bool
        :return: The same DataFrame for piping.
        :rtype: pd.DataFrame
        """
        self._df._initial_shape = self._df.shape
        if clone:
            self._df._initial_df = self._df.copy()
        else:
            self._df._initial_df = None
        return self._df

    def midlog(self, msg: str = "") -> pd.DataFrame:
        """
        Alias for `.endlog().startlog()`
        """
        return self.endlog(msg).startlog()

    def endlog(self, msg: str = "") -> pd.DataFrame:
        """
        Log changes to the DataFrame.

        :param msg: A custom message
        :type msg: str
        :return: The pandas Series for piping.
        :rtype: pd.Series
        """
        final_shape = self._df.shape
        initial_shape = self._df._initial_shape
        if final_shape != initial_shape:
            nrow0, ncol0 = initial_shape
            nrow1, ncol1 = final_shape
            dr = nrow0 - nrow1
            dc = ncol0 - ncol1
            if dr > 0:
                msg += f"Removed {dr:,d}/{nrow0:,d} ({dr / nrow0:.2%}) rows."
            elif dr < 0:
                dr = abs(dr)
                msg += f"Added {dr:,d}/{nrow0:,d} ({dr / nrow0:.2%}) rows."
            if dc > 0:
                msg += f"Removed {dc:,d}/{ncol0:,d} ({dc / ncol0:.2%}) columns."
            elif dc < 0:
                dc = abs(dc)
                msg += f"Added {dc:,d}/{ncol0:,d} ({dc / ncol0:.2%}) columns."
        else:
            initial_df = self._df._initial_df
            if initial_df is not None:
                nchanged = self._df != initial_df
                # missings are different than themselves
                # if both values are missing, set changed to False
                nchanged[self._df.isna() & initial_df.isna()] = False
                # Get total number of cells that have changed
                nchanged = nchanged.sum().sum()
                if nchanged == 0:
                    msg += "No changes detected."
                else:
                    ntot = initial_df.size
                    msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged / ntot:.2%}) values."
            else:
                msg += "Shape is the same. No value-level comparison done because clone=False was used in startlog()."
        logger.info(msg)
        del self._df._initial_df
        del self._df._initial_shape
        return self._df

    def add_prefix_if_not_exists(df, prefix: str) -> pd.DataFrame:
        """
        Add a prefix to all column names that do not already have it.
        
        :param prefix: The prefix to add
        :type prefix: str
        """
        new_cols = {
            col: f"{prefix}{col}"
            for col in df._df.columns
            if not col.startswith(prefix)
        }
        return df._df.rename(columns=new_cols)

    def get_duplicates(self, *args, **kwargs):
        mask = self._df.duplicated(*args, **kwargs)
        return self._df[mask]

    def sort_columns(self) -> pd.DataFrame:
        """
        Sort columns using natural sorting
        """
        self._df = self._df[natsorted(self._df.columns)]
        return self._df

    def freq(self, colname: str, dropna:bool=False) -> pd.DataFrame:
        """
        Generate frequency table for a variable.
        
        :param colname: The name of the column holding the variable
        :type colname: str
        :param dropna: Whether to drop missing values before generating frequency table
        :type dropna: bool
        :return: A DataFrame with the frequency table
        :rtype: pd.DataFrame
        """
        return self._df[colname].raffa.freq()

    def to_docx(
        self,
        outfp: Path,
        include_index: bool = True,
        docx_options: DocxOptions = DocxOptions(),
        table_style: str = "Table Grid",
        autofit: bool = True,
    ):
        # See: https://stackoverflow.com/a/40597684/1719931

        df = self._df

        doc = prepare_docx(docx_options)

        # Create table
        # One row is for the headers (i.e. columns names)
        n_rows, n_cols = df.shape[0] + 1, df.shape[1]
        if include_index:
            n_cols += 1

        t = doc.add_table(n_rows, n_cols)

        # add the header rows.
        for j in range(df.shape[-1]):
            if include_index:
                t.cell(0, j + 1).text = str(df.columns[j])
            else:
                t.cell(0, j).text = str(df.columns[j])

        # add index names
        if include_index:
            if df.index.name is not None:
                t.cell(0, 0).text = df.index.name
            for i in range(df.shape[0]):
                t.cell(i + 1, 0).text = str(df.index[i])

        # add the rest of the data frame
        for i in range(df.shape[0]):
            for j in range(df.shape[-1]):
                if include_index:
                    t.cell(i + 1, j + 1).text = str(df.values[i, j])
                else:
                    t.cell(i + 1, j).text = str(df.values[i, j])

        if autofit:
            doc = set_autofit(doc)

        # Set table style
        # See: https://github.com/python-openxml/python-docx/issues/9
        t.style = table_style

        # save the doc
        doc.save(outfp)


if __name__ == "__main__":
    # Run with `uv run python -P pandas.py -v`
    import doctest

    # doctest.testmod(optionflags=doctest.REPORT_NDIFF)
    doctest.testmod()
