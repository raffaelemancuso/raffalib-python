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
Internal helpers shared by the pandas and polars logging accessors.

These functions only build human-readable log messages; the
library-specific mechanics (metadata storage, cloning, value comparison)
stay in :mod:`raffalib.pandas` and :mod:`raffalib.polars`.
"""

import time
import datetime
import humanize

#: Message used when ``startlog(clone=False)`` prevents value-level comparison.
CLONE_FALSE_MSG = (
    "Shape is the same. No value-level comparison done because "
    "clone=False was used in startlog()."
)


def ratio(numerator: int, denominator: int) -> str:
    """
    Format ``numerator/denominator (percentage)``, guarding against a zero
    denominator.

    :param numerator: The count being described.
    :type numerator: int
    :param denominator: The total it is measured against.
    :type denominator: int
    :return: A string like ``"1/4 (25.00%)"``, or ``"0/0 (N/A)"`` when
        ``denominator`` is zero.
    :rtype: str
    """
    if denominator == 0:
        return f"{numerator:,d}/{denominator:,d} (N/A)"
    return f"{numerator:,d}/{denominator:,d} ({numerator / denominator:.2%})"


def count_delta(delta: int, total: int, unit: str) -> str:
    """
    Describe a signed count change along a single dimension.

    :param delta: ``initial - final`` count. Positive means items were removed,
        negative means items were added.
    :type delta: int
    :param total: The initial count, used as the denominator for the percentage.
    :type total: int
    :param unit: Name of the items being counted (e.g. ``"rows"``, ``"values"``).
    :type unit: str
    :return: A message like ``"Removed 5/10 (50.00%) rows."``, or an empty
        string when ``delta`` is zero.
    :rtype: str
    """
    if delta > 0:
        return f"Removed {ratio(delta, total)} {unit}."
    if delta < 0:
        return f"Added {ratio(abs(delta), total)} {unit}."
    return ""


def dataframe_shape_delta(
    initial_shape: tuple[int, int], final_shape: tuple[int, int]
) -> str:
    """
    Describe how a DataFrame's row and column counts changed.

    :param initial_shape: ``(n_rows, n_cols)`` before the operation.
    :type initial_shape: tuple[int, int]
    :param final_shape: ``(n_rows, n_cols)`` after the operation.
    :type final_shape: tuple[int, int]
    :return: The concatenated row and column change messages.
    :rtype: str
    """
    nrow0, ncol0 = initial_shape
    nrow1, ncol1 = final_shape
    return count_delta(nrow0 - nrow1, nrow0, "rows") + count_delta(
        ncol0 - ncol1, ncol0, "columns"
    )


def changed_cells(nchanged: int, ntotal: int) -> str:
    """
    Describe how many cells changed when the shape stayed the same.

    :param nchanged: Number of cells whose value changed.
    :type nchanged: int
    :param ntotal: Total number of cells.
    :type ntotal: int
    :return: ``"No changes detected."`` or a message like
        ``"Changed 3/12 (25.00%) values."``.
    :rtype: str
    """
    if nchanged == 0:
        return "No changes detected."
    return f"Changed {ratio(nchanged, ntotal)} values."


def elapsed(start_time_ns: int) -> str:
    """
    Describe the elapsed time since a ``time.perf_counter_ns()`` reading.

    :param start_time_ns: A start timestamp from :func:`time.perf_counter_ns`.
    :type start_time_ns: int
    :return: A message like ``"\\nTook: 1.20 seconds"``.
    :rtype: str
    """
    diff = datetime.timedelta(
        microseconds=(time.perf_counter_ns() - start_time_ns) / 1000
    )
    return "\nTook: " + humanize.precisedelta(diff)
