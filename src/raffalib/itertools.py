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

def batch_boundaries(total, n_per_batch):
    """
    Yield (batchi, start_ix, end_ix) for batches of size n_per_batch.
    Example:
    list(batch_boundaries(20, 3))
    [(0, 1, 3), (1, 4, 6), (2, 7, 9), (3, 10, 12), (4, 13, 15), (5, 16, 18), (6, 19, 20)]
    """
    start_ixs = list(range(1, total, n_per_batch))
    for batchi, start_ix in enumerate(start_ixs):
        end_ix = min(total, start_ix + n_per_batch - 1)
        yield batchi, start_ix, end_ix