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

# Also useful for SeleniumBase

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

def scroll_into_view_js(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def scroll_into_view(driver, element):
    ActionChains(driver).move_to_element(element).perform()

def scroll_delta(driver, element, delta_x, delta_y):
    scroll_origin = ScrollOrigin.from_element(element)
    ActionChains(driver)\
        .scroll_from_origin(scroll_origin, delta_x, delta_y)\
        .perform()
    
def wait_element_to_be_visible(driver, element, timeout=10):
    WebDriverWait(driver, timeout).until(EC.visibility_of(element))
    
def wait_element_to_be_clickable(driver, element, timeout=10):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
