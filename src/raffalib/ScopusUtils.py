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

from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import re
import logging

class ScopusUtils:

    def __init__(self):
        self.ua = UserAgent()

    def get_new_scopus_id(self, old_scopus_id):
            def get_match(old_scopus_id):
                headers = {"User-Agent":self.ua.chrome}
                url = "https://www.scopus.com/authid/detail.uri?authorId="+old_scopus_id
                for _ in range(5):
                    resp = requests.get(url, headers=headers)
                    assert(resp.status_code==200)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    match = re.search(r'nonTombstonedAuthorId="(\d+)"', resp.text)
                    if match is None:
                        time.sleep(2)
                    else:
                        return match
                logging.error(f"HTML is malformed: {url}")
                raise Exception("Malformed HTML")
            match = get_match(old_scopus_id)
            new_id = match.group(1)
            logging.info(f"Downloaded new Scopus ID: {old_scopus_id} -> {new_id}")
            if new_id=="0":
                return old_scopus_id
            assert(new_id.isdigit())
            assert(10<=len(new_id)<=11)
            return new_id
