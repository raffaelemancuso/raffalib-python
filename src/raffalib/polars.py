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
from enum import Enum, auto
import logging
import copy
import time
import datetime
import humanize

pl.Config(thousands_separator=",")
logger_name = "polars_raffa"


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

    def endlog(self):
        if "old_shape" not in self._df._series.get_metadata():
            logging.getLogger(logger_name).info(
                "You have to call startlog() before calling endlog()."
            )
            return self._series
        custom_msg = self._series.config_meta.get_metadata()["custom_msg"]
        if custom_msg is None:
            custom_msg = ""
        else:
            custom_msg += ". "
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
                msg = f"{custom_msg}Shape is the same. No value-level comparison done because clone=False was used in startlog()."
            else:
                a = (self._df != old_series).fill_null(False).to_numpy()
                b = (
                    self._df.with_columns(pl.all().is_null())
                    != old_series.with_columns(pl.all().is_null())
                ).to_numpy()
                n_changed = (a | b).sum()
                n_values = old_shape[0]
                msg = f"{custom_msg}Shape is the same. Values changed: {n_changed:,d}/{n_values:,d} ({n_changed / n_values:.2%})."
        end_time = time.perf_counter_ns()
        elapsed = end_time - start_time
        diff = datetime.timedelta(microseconds=elapsed / 1000)
        msg += "\nTook: " + humanize.precisedelta(diff)
        logging.getLogger(logger_name).info(msg)
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

    def startlog(self, custom_msg=None, clone=False):
        self._df.config_meta.set(custom_msg=custom_msg)
        self._df.config_meta.set(old_shape=self._df.shape)
        self._df.config_meta.set(start_time=time.perf_counter_ns())
        if clone:
            self._df.config_meta.set(old_df=self._df.clone())
        else:
            self._df.config_meta.set(old_df=None)
        return self._df

    def endlog(self):
        if "old_shape" not in self._df.config_meta.get_metadata():
            logging.getLogger(logger_name).info(
                "You have to call startlog() before calling endlog()."
            )
            return self._df
        custom_msg = self._df.config_meta.get_metadata()["custom_msg"]
        if custom_msg is None:
            custom_msg = ""
        else:
            custom_msg += ". "
        start_time = self._df.config_meta.get_metadata()["start_time"]
        old_shape = self._df.config_meta.get_metadata()["old_shape"]
        new_shape = self._df.shape
        if new_shape != old_shape:
            dr = new_shape[0] - old_shape[0]
            dc = new_shape[1] - old_shape[1]
            msg = (
                f"{custom_msg}"
                f"Rows variation: {dr:,d}/{old_shape[0]:,d} ({dr / old_shape[0]:.2%}).\n"
                f"Columns variation: {dc:,d}/{old_shape[1]:,d} ({dc / old_shape[1]:.2%})."
            )
        else:
            old_df = self._df.config_meta.get_metadata()["old_df"]
            if old_df is None:
                msg = f"{custom_msg}Shape is the same. No value-level comparison done because clone=False was used in startlog()."
            else:
                a = (self._df != old_df).fill_null(False).to_numpy()
                b = (
                    self._df.with_columns(pl.all().is_null())
                    != old_df.with_columns(pl.all().is_null())
                ).to_numpy()
                n_changed = (a | b).sum().sum()
                n_values = old_shape[0] * old_shape[1]
                msg = f"{custom_msg}Shape is the same. Values changed: {n_changed:,d}/{n_values:,d} ({n_changed / n_values:.2%})."
        end_time = time.perf_counter_ns()
        elapsed = end_time - start_time
        diff = datetime.timedelta(microseconds=elapsed / 1000)
        msg += "\nTook: " + humanize.precisedelta(diff)
        logging.getLogger(logger_name).info(msg)
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

    def join(self, df2, *args, keep_source: bool = False, log_col_changes=False, **kwargs):
        left_col = "source_left"
        right_col = "source_right"
        # Get DataFrame to join, add source column
        df1 = self._df.with_columns(pl.lit(True).alias(left_col))
        df2 = df2.with_columns(pl.lit(True).alias(right_col))
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
            logging.getLogger(logger_name).info(
                f"Detected filtering join. "
                f"Rows variation {n_var:,d}/{n_initial:,d} ({n_var / n_initial:.2%}), "
                f"total rows after join: {n_rows_joined:,d}/{n_initial:,d} ({n_rows_joined / n_initial:.2%})"
            )
            joined = joined.drop([left_col])
            return joined
        # Detect how many rows in the output table are present in the input tables
        joined = joined.with_columns(
            pl.col([left_col, right_col]).fill_null(False)
        )
        n_both = joined.filter(pl.col(left_col), pl.col(right_col)).shape[0]
        n_left_only = joined.filter(
            pl.col(left_col), ~pl.col(right_col)
        ).shape[0]
        n_right_only = joined.filter(
            ~pl.col(left_col), pl.col(right_col)
        ).shape[0]
        # Log rows information
        msg = f"Total rows in output table: {n_rows_joined:,d}\n"
        msg += f"\tFrom left: {n_left_only:,d} ({n_left_only / n_rows_joined:.2%})\n"
        msg += f"\tFrom right: {n_right_only:,d} ({n_right_only / n_rows_joined:.2%})\n"
        msg += f"\tFrom both: {n_both:,d} ({n_both / n_rows_joined:.2%})\n"
        # Detect added and removed columns
        if log_col_changes:
            cols_out = set(joined.columns)
            cols_left = set(df1.columns)
            cols_right = set(df2.columns)
            msg += f"Columns in output table not in left table: {cols_out - cols_left})\n"
            msg += f"Columns in output table not in right table: {cols_out - cols_right})"
        logging.getLogger(logger_name).info(msg)
        # Add a column that indicate where that row comes from
        if keep_source:
            joined = joined.with_columns(
                pl.when(pl.col.source_left & pl.col.source_right)
                .then(pl.lit("both"))
                .when(pl.col.source_left & ~pl.col.source_right)
                .then(pl.lit("left_only"))
                .when(~pl.col.source_left & pl.col.source_right)
                .then(pl.lit("right_only"))
                .otherwise(pl.lit("error"))
                .alias("source")
            )
            joined = joined.permute.append(["source"])
        # Drop source columns and return
        joined = joined.drop([left_col, right_col])
        return joined
