
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from tortoises.agent import get_user_agent


def init_option(headless=True, limit=True):
    options = Options()
    options.add_argument(f'--user-agent={get_user_agent(random=True)}')
    if limit:
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
    if headless:
        options.add_argument('--headless')
    return options


def start_chrome(headless=True, limit=True, delete_cookies=True, *args, **kwargs):
    chrome_options = init_option(headless=headless, limit=limit)
    chrome_driver = webdriver.Chrome(options=chrome_options, *args, **kwargs)
    if delete_cookies:
        chrome_driver.delete_all_cookies()
    return chrome_driver


class MyWebDriver(WebDriver):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def find_element_by_class_name(self, name):
        element = None
        try:
            element = super().find_element_by_class_name(name)
        except NoSuchElementException:
            pass
        return element

    def find_element_by_id(self, id_):
        element = None
        try:
            element = super().find_element_by_id(id_)
        except NoSuchElementException:
            pass
        return element

    def find_element_by_xpath(self, xpath):
        element = None
        try:
            element = super().find_element_by_xpath(xpath)
        except NoSuchElementException:
            pass
        return element


def start_my_chrome(headless=True, limit=True, *args, **kwargs):
    chrome_options = init_option(headless=headless, limit=limit)
    chrome_driver = MyWebDriver(options=chrome_options, *args, **kwargs)
    chrome_driver.delete_all_cookies()
    return chrome_driver


if __name__ == '__main__':

    driver = start_my_chrome()
    driver.get('http://www.baidu.com/')

    driver.find_element_by_class_name('nothing')
    driver.find_element_by_class_name('s_ipt')
