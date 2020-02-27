
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from tortoises.agent import get_user_agent


def start_chrome(headless=True, *args):
    """
    :param headless: whether to launch browser interface
    """
    # browser options
    chrome_options = Options()
    chrome_options.add_argument(f'--user-agent={get_user_agent(random=True)}')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    if headless:
        chrome_options.add_argument('--headless')

    # launch chrome driver
    chrome_driver = webdriver.Chrome(options=chrome_options, *args)
    # delete cookies
    chrome_driver.delete_all_cookies()

    return chrome_driver
