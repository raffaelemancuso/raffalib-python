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

# copied from https://stackoverflow.com/a/93029/1719931
import unicodedata, re, itertools, sys

all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {'Cc'}
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) in categories)
# or equivalently and much more efficiently
#control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))

hyphens = re.compile(r'-\n')
control_char_re = re.compile('[%s]' % re.escape(control_chars))
multiple_spaces_re = re.compile(r'\s+')

def preprocess_text_for_rag(s):
    s = hyphens.sub('', s)
    s = control_char_re.sub(' ', s)
    s = multiple_spaces_re.sub(' ', s)    
    return s