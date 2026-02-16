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

import logging
from rich.logging import RichHandler

def create_logger(app_name:str="myapp"):
    logging.captureWarnings(True)
    logger = logging.getLogger(app_name)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    #handler = logging.StreamHandler(stream=sys.stdout)
    handler = RichHandler(rich_tracebacks=True)
    fmt = logging.Formatter(
        #fmt="{asctime} - {name} - {levelname} - {message}",
        # rich already prints the timestamp
        fmt="{name} - {levelname}\n{message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    #If this attribute evaluates to true, 
    # events logged to this logger will be passed to the handlers of higher level (ancestor) loggers, 
    # in addition to any handlers attached to this logger. 
    # Messages are passed directly to the ancestor loggers’ handlers 
    # - neither the level nor filters of the ancestor loggers in question are considered.
    logger.propagate = False
    return(logger)