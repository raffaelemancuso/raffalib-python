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

import requests
import logging
import pyalex
import datetime


def check_openalex_api_key():
    """
    Check if the OpenAlex API key is valid.

    :return: True if the API key is valid (can access the API), False if access is denied (403).
    :rtype: bool
    :raises requests.exceptions.HTTPError: For HTTP errors other than 403.

    .. note::
        Requires the pyalex package and a valid OPENALEX_API_KEY environment variable.
    """
    bk_cods = pyalex.config.retry_http_codes
    pyalex.config.retry_http_codes = None
    dt = f"{datetime.datetime.now().year}-01-01"
    try:
        pyalex.Works().filter(from_updated_date=dt).get()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return False
        logging.error(f"Unexpected HTTP error: {e}")
        raise
    else:
        return True
    finally:
        pyalex.config.retry_http_codes = bk_cods
