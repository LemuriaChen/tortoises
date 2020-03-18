
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from .agent import get_user_agent


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


def start_chrome(headless=True, limit=True, delete_cookies=True, maximize=True, enigma=False):
    chrome_options = init_option(headless=headless, limit=limit)
    if enigma:
        chrome_driver = EnigmaWebDriver(options=chrome_options)
    else:
        chrome_driver = webdriver.Chrome(options=chrome_options)
    if delete_cookies:
        chrome_driver.delete_all_cookies()
    if maximize:
        chrome_driver.maximize_window()
    return chrome_driver


def start_firefox():
    firefox_driver = webdriver.Firefox()
    return firefox_driver


def start_phantomjs():
    phantomjs_driver = webdriver.PhantomJS()
    return phantomjs_driver


class EnigmaWebDriver(WebDriver):

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


if __name__ == '__main__':

    driver = start_chrome(enigma=True)
    driver.get('http://www.baidu.com/')

    driver.find_element_by_class_name('nothing')
    driver.find_element_by_class_name('s_ipt')

