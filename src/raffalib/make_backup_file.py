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

import datetime
import logging
from pathlib import Path

def make_backup_file(fp: Path) -> None:
    """Move file to a backup."""
    if not fp.exists():
        logging.warning(f"File {fp} does not exist, skipping backup.")
        return
    mtime = fp.stat().st_mtime
    new_stem = f"{fp.stem}_{datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d-%H-%M-%S')}"
    backup_file = fp.with_stem(f"{new_stem}")
    fp.rename(backup_file)
