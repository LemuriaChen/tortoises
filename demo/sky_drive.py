

from tortoises.driver import start_chrome

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import json
from tqdm import tqdm


class SkyDrive(object):

    def __init__(self, headless=False, limit=False):
        self.driver = start_chrome(headless=headless, limit=limit)

    def login(self):
        print('login < https://pan.baidu.com/ > ...')
        try:
            self.driver.get('https://pan.baidu.com/')
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div")))
            time.sleep(2)
        except TimeoutException:
            raise TimeoutException
        print('success to login')

    def save_cookie(self, cookie_path='cookie/drive_cookie.txt'):
        # save cookie
        print('saving cookies to path < cookie/drive_cookie.txt >')
        with open(cookie_path, 'w') as f:
            f.write(json.dumps(self.driver.get_cookies()))

    def login_with_cookie(self, cookie_path='cookie/drive_cookie.txt'):
        self.login()
        # add cookie
        print('loading cookies from path < cookie/drive_cookie.txt >')
        with open(cookie_path, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)

        print('refreshing browser')
        self.driver.refresh()
        WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div")))
        time.sleep(10)

        print('maximizing browser window')
        self.driver.maximize_window()
        time.sleep(5)
        return self

    def save(self, url, pwd, save_dir='Books'):

        try:
            print(f'saving info: '
                  f'\n\tsky drive link: {url}'
                  f'\n\tverification code: {pwd}'
                  f'\n\tsaving directory: \'{save_dir}\'')
            # get url

            self.driver.get(url)
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div")))

            # input password
            self.driver.find_element_by_xpath('//input').send_keys(pwd)
            # click
            self.driver.find_element_by_class_name('g-button-right').click()
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div[@node-type='fydGNC']")))
            time.sleep(2)

            # select all
            selector = self.driver.find_element_by_xpath("//div[@node-type='fydGNC']")
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(2)

            # save
            selector = self.driver.find_element_by_class_name('g-button')
            self.driver.execute_script('arguments[0].click()', selector)
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='file-tree-container']")))
            time.sleep(2)

            # optional save path
            selector = self.driver.find_element_by_xpath(
                f"//div[@class='file-tree-container']/ul/li/ul/li//*[text()='{save_dir}']"
            )
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(2)

            selector = self.driver.find_element_by_xpath("//a[@title='确定']")
            self.driver.execute_script('arguments[0].click()', selector)

            time.sleep(2)

            if '已为您成功保存文件' in self.driver.page_source:
                print('success to save')

        except Exception as e:
            print(e)

    def close(self):
        self.driver.close()


if __name__ == '__main__':

    import pandas as pd
    links = pd.read_csv('link.txt', header=None)

    sd = SkyDrive(headless=False, limit=False).login_with_cookie()

    for _, line in tqdm(links.iterrows()):
        sd.save(url=line[0], pwd=line[1])


"""
Selenium — 点击被页面上其他元素遮住的控件
点击被页面上其他元素遮住的控件
使用WebDriver点击界面上Button元素时，如果当前Button元素被界面上其他元素遮住了
或没出现在界面中（比如Button在页面底部，但是屏幕只能显示页面上半部分）
使用默认的WebElement.Click()可能会触发不了Click事件
需加上browser.execute_script(‘arguments[0].click()’, webElement);
"""
