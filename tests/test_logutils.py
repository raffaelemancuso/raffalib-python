import time

from raffalib import _logutils


def test_clone_false_msg():
    assert _logutils.CLONE_FALSE_MSG == (
        "Shape is the same. No value-level comparison done because "
        "clone=False was used in startlog()."
    )


def test_count_delta_removed():
    assert _logutils.count_delta(1, 4, "rows") == "Removed 1/4 (25.00%) rows."


def test_count_delta_added():
    assert _logutils.count_delta(-2, 4, "values") == "Added 2/4 (50.00%) values."


def test_count_delta_zero_is_empty():
    assert _logutils.count_delta(0, 4, "rows") == ""


def test_count_delta_added_to_empty_is_guarded():
    # Adding rows to an initially-empty frame: denominator is zero.
    assert _logutils.count_delta(-3, 0, "rows") == "Added 3/0 (N/A) rows."


def test_count_delta_thousands_separator():
    assert (
        _logutils.count_delta(1500, 3000, "rows")
        == "Removed 1,500/3,000 (50.00%) rows."
    )


def test_dataframe_shape_delta_rows_and_columns():
    msg = _logutils.dataframe_shape_delta((10, 5), (8, 6))
    assert msg == "Removed 2/10 (20.00%) rows.Added 1/5 (20.00%) columns."


def test_dataframe_shape_delta_rows_only():
    assert (
        _logutils.dataframe_shape_delta((10, 5), (7, 5))
        == "Removed 3/10 (30.00%) rows."
    )


def test_dataframe_shape_delta_no_change_is_empty():
    assert _logutils.dataframe_shape_delta((10, 5), (10, 5)) == ""


def test_ratio_basic():
    assert _logutils.ratio(1, 4) == "1/4 (25.00%)"


def test_ratio_negative_numerator():
    assert _logutils.ratio(-2, 5) == "-2/5 (-40.00%)"


def test_ratio_thousands_separator():
    assert _logutils.ratio(1500, 3000) == "1,500/3,000 (50.00%)"


def test_ratio_zero_denominator_guarded():
    assert _logutils.ratio(0, 0) == "0/0 (N/A)"


def test_changed_cells_none():
    assert _logutils.changed_cells(0, 12) == "No changes detected."


def test_changed_cells_some():
    assert _logutils.changed_cells(3, 12) == "Changed 3/12 (25.00%) values."


def test_elapsed_prefix_and_type():
    msg = _logutils.elapsed(time.perf_counter_ns())
    assert isinstance(msg, str)
    assert msg.startswith("\nTook: ")
