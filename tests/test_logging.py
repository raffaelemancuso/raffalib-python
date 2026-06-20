import logging

from raffalib.logging import create_logger


def test_returns_named_logger():
    lg = create_logger(
        "raffalib_test_logger", level="INFO", disable_existing_loggers=False
    )
    assert isinstance(lg, logging.Logger)
    assert lg.name == "raffalib_test_logger"


def test_root_logger_when_name_empty():
    lg = create_logger("", level="WARNING", disable_existing_loggers=False)
    assert isinstance(lg, logging.Logger)


def test_keeps_accessor_loggers_enabled():
    create_logger("whatever", level="INFO", disable_existing_loggers=False)
    assert logging.getLogger("raffalib.pandas").disabled is False
    assert logging.getLogger("raffalib.polars").disabled is False
