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

import polars as pl
import polars.selectors as cs
import polars_config_meta
import polars_permute
from enum import Enum, auto
import logging
import copy
import time
import datetime
import humanize

logger = logging.getLogger(__name__)
pl.Config(thousands_separator=",")

class PercOptions(Enum):
    NO = auto()
    TOTAL = auto()
    COLUMNS = auto()
    ROWS = auto()

@pl.api.register_series_namespace("raffa")
class RaffaPolarsSeriesUtils:
    def __init__(self, series: pl.Series):
        self._series = series
        
    def startlog(self, custom_msg=None, clone=False):
        self._series.config_meta.set(custom_msg=custom_msg)
        self._series.config_meta.set(old_shape=self._series.shape)
        self._series.config_meta.set(start_time=time.perf_counter_ns())
        if clone:
            self._series.config_meta.set(old_series=self._series.clone())
        else:
            self._series.config_meta.set(old_series=None)
        return self._series

    def endlog(self, timeit=True):
        if "old_shape" not in self._df._series.get_metadata():
            logger.info(
                "You have to call startlog() before calling endlog()."
            )
            return self._series
        custom_msg = self._series.config_meta.get_metadata()["custom_msg"]
        if custom_msg is None:
            custom_msg = ""
        else:
            custom_msg += ". "
        msg = f"{custom_msg}"
        
        start_time = self._series.config_meta.get_metadata()["start_time"]
        old_shape = self._series.config_meta.get_metadata()["old_shape"]
        new_shape = self._series.shape
        
        if new_shape != old_shape:
            dr = new_shape[0] - old_shape[0]
            msg = (
                f"{custom_msg}"
                f"Variation: {dr:,d}/{old_shape[0]:,d} ({dr / old_shape[0]:.2%}).\n"
            )
            
        else:
            old_series = self._series.config_meta.get_metadata()["old_series"]
            if old_series is None:
                msg += f"Shape is the same. No value-level comparison done because clone=False was used in startlog()."
            else:
                a = (self._df != old_series).fill_null(False).to_numpy()
                b = (
                    self._df.with_columns(pl.all().is_null())
                    != old_series.with_columns(pl.all().is_null())
                ).to_numpy()
                n_changed = (a | b).sum()
                n_values = old_shape[0]
                msg += f"Shape is the same. Values changed: {n_changed:,d}/{n_values:,d} ({n_changed / n_values:.2%})."
        
        if timeit:
            end_time = time.perf_counter_ns()
            elapsed = end_time - start_time
            diff = datetime.timedelta(microseconds=elapsed / 1000)
            msg += "\nTook: " + humanize.precisedelta(diff)
            
        logger.info(msg)
        return self._series

    def freq(self) -> pl.DataFrame:
        tot = self._series.shape[0]
        counter = (
            self._series.value_counts()
            .select(cs.by_index(0).cast(pl.String).alias("value"), "count")
            .with_columns(((pl.col("count") / tot) * 100).alias("perc"))
            .sort("perc", descending=True)
        )
        tot_row = pl.DataFrame(
            {
                "value": ["Total"],
                "count": [counter.get_column("count").sum()],
                "perc": [counter.get_column("perc").sum()],
            },
            schema={"value": pl.Utf8, "count": pl.UInt32, "perc": pl.Float64},
        )
        counter = pl.concat([counter, tot_row], how="vertical")
        return counter

    def crosstab(
        self, ser_b: pl.Series, perc: PercOptions = PercOptions.NO
    ) -> pl.DataFrame:
        df = pl.DataFrame({self._series.name: self._series, ser_b.name: ser_b})
        return df.raffa.crosstab(self._series.name, ser_b.name, perc=perc)


@pl.api.register_dataframe_namespace("raffa")
class RaffaPolarsDataFrameUtils:
    
    def __init__(self, df: pl.DataFrame):
        self._df = df

    def startlog(self, clone=False) -> pl.DataFrame:
        """
        Initialize the logger.

        :param clone: Whether to clone the series. Takes more RAM but allows logging of changed values. Otherwise, only changed shapes is logged.
        :type clone: bool
        :return: The same DataFrame for piping.
        :rtype: pl.DataFrame
        """
        
        self._df.config_meta.set(initial_shape=self._df.shape, start_time=time.perf_counter_ns())
        if clone:
            self._df.config_meta.set(initial_df=self._df.clone())
        else:
            self._df.config_meta.set(initial_df=None)
        return self._df

    def endlog(self, custom_msg:str|None = None, timeit:bool=True) -> pl.DataFrame:
        """
        Log changes to the DataFrame.

        :param msg: A custom message to log before the actual log
        :type msg: str
        :param timeit: Log the time it took for the operation
        :type timeit: bool
        :return: The DataFrame for piping.
        :rtype: pl.DataFrame
        """
        
        if "initial_shape" not in self._df.config_meta.get_metadata():
            logger.info(
                "You have to call startlog() before calling endlog()."
            )
            return self._df
        initial_shape = self._df.config_meta.get_metadata()["initial_shape"]
        
        custom_msg = self._df.config_meta.get_metadata()["custom_msg"]
        if custom_msg is None:
            custom_msg = ""
        else:
            custom_msg += ". "
        msg = f"{custom_msg}"
        start_time = self._df.config_meta.get_metadata()["start_time"]
        
        final_shape = self._df.shape
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
            initial_df = self._df.config_meta.get_metadata()["initial_df"]
            if initial_df is None:
                msg += "Shape is the same. No value-level comparison done because clone=False was used in startlog()."
            else:
                a = (self._df != initial_df).fill_null(False).to_numpy()
                b = (
                    self._df.with_columns(pl.all().is_null())
                    != initial_df.with_columns(pl.all().is_null())
                ).to_numpy()
                # Get total number of cells that have changed
                nchanged = (a | b).sum().sum()   
                if(nchanged == 0):
                    msg += "No changes detected."
                else:
                    ntot = final_shape[0] * final_shape[1]
                    msg += f"Changed {nchanged:,d}/{ntot:,d} ({nchanged/ntot:.2%}) values."
        if timeit:
            end_time = time.perf_counter_ns()
            elapsed = end_time - start_time
            diff = datetime.timedelta(microseconds=elapsed / 1000)
            msg += "\nTook: " + humanize.precisedelta(diff)
        logger.info(msg)
        return self._df
        
    def replace_string_with_null(self, s):
        # self._df.with_columns(pl.col(pl.String).str.replace(s, None).name.keep())
        self._df = self._df.with_columns(pl.when(pl.col(pl.String) == s).then(None).otherwise(pl.col(pl.String)).name.keep())
        return self._df
        
    def freq(self, col, *args, **kwargs) -> pl.DataFrame:
        return self._df.get_column(col).raffa.freq(*args, **kwargs)

    def crosstab(
        self, col_a: str, col_b: str, perc: PercOptions = PercOptions.NO
    ) -> pl.DataFrame:
        ct = self._df.pivot(
            on=col_b,
            index=col_a,
            values=col_b,
            aggregate_function="len",
            sort_columns=True,
        ).sort(col_a)

        if perc == PercOptions.NO:
            return ct

        values = ~cs.first()

        options = {
            PercOptions.COLUMNS: values.sum(),
            PercOptions.ROWS: pl.sum_horizontal(values),
            PercOptions.TOTAL: pl.sum_horizontal(values).sum(),
        }

        return ct.with_columns(values / options[perc] * 100)

    def join(self, df2:pl.DataFrame, *args, keep_row_index: bool = False, log_col_changes=False, **kwargs):
        """
        Wrapper around `pl.DataFrame.join` to log join operations.

        :param df2: The dataframe on the right of the join
        :type df2: pl.DataFrame
        :param *args: Additional position arguments passed to `pl.DataFrame.join`
        :type *args: Any
        :param keep_row_index: Whether to keep columns indicating the row index of the source table in the output table
        :type keep_row_index: bool
        :param log_col_changes: Whether to log column changes
        :type log_col_changes: bool
        :param *kwargs: Additional keyword arguments passed to `pl.DataFrame.join`
        :type *kwargs: Any
        :return: The joined DataFrame
        :rtype: pl.DataFrame
        """
        
        left_col = "source_left"
        right_col = "source_right"
        # Get DataFrame to join, add source column
        df1 = self._df.with_row_index(left_col)
        df2 = df2.with_row_index(right_col)
        # Join DataFrames
        joined = df1.join(df2, *args, **kwargs)
        n_rows_joined = joined.shape[0]
        # Check whether this is a filtering join
        # Filtering joins filter rows from x based on the presence or absence of matches in y:
        # semi_join() return all rows from x with a match in y.
        # anti_join() return all rows from x without a match in y.
        is_filter = kwargs.get("how", None) in ["anti", "semi"]
        # If this is a filtering join, log only the rows variation in the left table
        if is_filter:
            n_initial = df1.shape[0]
            n_var = n_rows_joined - n_initial
            logger.info(
                f"Detected filtering join. "
                f"Rows variation {n_var:,d}/{n_initial:,d} ({n_var / n_initial:.2%}), "
                f"total rows after join: {n_rows_joined:,d}/{n_initial:,d} ({n_rows_joined / n_initial:.2%})"
            )
            joined = joined.drop([left_col])
            return joined
        # Detect how many rows in the output table are present in the input tables
        joined_both = joined.filter(~pl.col(left_col).is_null(), ~pl.col(right_col).is_null())
        n_both = joined_both.shape[0]
        n_left_dups = joined_both.get_column(left_col).is_duplicated().sum()
        n_right_dups = joined_both.get_column(right_col).is_duplicated().sum()
        n_left_only = joined.filter(
            ~pl.col(left_col).is_null(), pl.col(right_col).is_null()
        ).shape[0]
        n_right_only = joined.filter(
            pl.col(left_col).is_null(), ~pl.col(right_col).is_null()
        ).shape[0]
        # Log rows information
        msg = f"Total rows in output table: {n_rows_joined:,d}\n"
        msg += f"From left only: {n_left_only:,d}/{n_rows_joined:,d} ({n_left_only / n_rows_joined:.2%})\n"
        msg += f"From right only: {n_right_only:,d}/{n_rows_joined:,d} ({n_right_only / n_rows_joined:.2%})\n"
        msg += f"From both: {n_both:,d}/{n_rows_joined:,d} ({n_both / n_rows_joined:.2%}) (left dups {n_left_dups}, right dups {n_right_dups})\n"
        # Detect added and removed columns
        if log_col_changes:
            cols_out = set(joined.columns)
            cols_left = set(df1.columns)
            cols_right = set(df2.columns)
            msg += f"Columns in output table not in left table: {cols_out - cols_left})\n"
            msg += f"Columns in output table not in right table: {cols_out - cols_right})"
        logger.info(msg)
        # Drop row indices
        if not keep_row_index:
            joined = joined.drop([left_col, right_col])
        else:
            joined = joined.permute.append([left_col, right_col])
        return joined

if __name__ == "__main__":
    # Run with `uv run python -P polars.py -v`
    import doctest
    #doctest.testmod(optionflags=doctest.REPORT_NDIFF)
    doctest.testmod()