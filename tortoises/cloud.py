
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import json
import random

from tortoises.driver import start_chrome


class CloudDisk(object):

    def __init__(self, user_name=None, password=None, maximize=True, *args, **kwargs):
        self.driver = start_chrome(*args, **kwargs)
        self.user_name = user_name
        self.password = password
        self.adjust(refresh=False, maximize=maximize)

    def fetch_home(self):
        print('login < https://pan.baidu.com/ > ...')
        try:
            self.driver.get('https://pan.baidu.com/')
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.ID, "TANGRAM__PSP_4__footerULoginBtn")))
            time.sleep(random.uniform(1, 3))
        except TimeoutException:
            raise TimeoutException
        print('success to login')

    def manual_login(self):
        self.driver = start_chrome(headless=True, limit=True)
        self.fetch_home()

    def login(self):
        assert self.user_name and self.password, 'user_name and password can\'t not be empty !'
        self.fetch_home()
        # 切换账号密码登陆
        try:
            selector = self.driver.find_element_by_id('TANGRAM__PSP_4__footerULoginBtn')
            self.driver.execute_script('arguments[0].click()', selector)
        except NoSuchElementException:
            pass
        # 输入账号密码并提交表单
        try:
            self.driver.find_element_by_id('TANGRAM__PSP_4__userName').send_keys(self.user_name)
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_id('TANGRAM__PSP_4__password').send_keys(self.password)
            time.sleep(random.uniform(1, 2))
            #
            selector = self.driver.find_element_by_id('TANGRAM__PSP_4__submit')
            self.driver.execute_script('arguments[0].click()', selector)
        except NoSuchElementException:
            pass
        self.get_account_info()

    def save_cookie(self, cookie_path='cookie/drive_cookie.txt'):
        # save cookie
        print(f'saving cookies to path < {cookie_path} >')
        with open(cookie_path, 'w') as f:
            f.write(json.dumps(self.driver.get_cookies()))

    def login_with_cookie(self, cookie_path='cookie/drive_cookie.txt'):
        assert cookie_path, 'cookie path can\'t not be empty !'
        self.fetch_home()
        # add cookie
        print(f'loading cookies from path < {cookie_path} >')
        with open(cookie_path, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)
        self.adjust(refresh=True, maximize=False)
        self.get_account_info()
        # return self

    def adjust(self, refresh: bool, maximize: bool):
        # refreshing browser
        if refresh:
            try:
                self.driver.refresh()
                WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "user-name")))
                time.sleep(random.uniform(1, 2))
            except TimeoutException:
                pass
        # maximizing browser window
        if maximize:
            self.driver.maximize_window()
            time.sleep(random.uniform(1, 2))

    def get_account_info(self):
        # 账号信息
        try:
            print(f"user_name: {self.driver.find_element_by_class_name('user-name').text}")
            print(f"space: {self.driver.find_element_by_class_name('remaining-space').text}")
        except NoSuchElementException:
            # print('fail to login, please try manual login')
            pass

    def save(self, url, pwd, save_dir='Books', verbose=True):

        try:
            if verbose:
                print(f'saving info: '
                      f'\n\tsky drive link: {url}'
                      f'\n\tverification code: {pwd}'
                      f'\n\tsaving directory: \'{save_dir}\'')

            # get url
            self.driver.get(url)
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//input")))
            time.sleep(random.uniform(1, 2))

            # input password
            self.driver.find_element_by_xpath('//input').send_keys(pwd)
            time.sleep(random.uniform(0.5, 1))

            # click
            selector = self.driver.find_element_by_class_name('g-button-right')
            self.driver.execute_script('arguments[0].click()', selector)
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div[@node-type='fydGNC']")))
            time.sleep(random.uniform(1, 3))

            # select all
            selector = self.driver.find_element_by_xpath("//div[@node-type='fydGNC']")
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(random.uniform(0.5, 1))

            # save
            selector = self.driver.find_element_by_class_name('g-button')
            self.driver.execute_script('arguments[0].click()', selector)
            WebDriverWait(driver=self.driver, timeout=100, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='file-tree-container']")))
            time.sleep(random.uniform(1, 3))

            # optional save path
            selector = self.driver.find_element_by_xpath(
                f"//div[@class='file-tree-container']/ul/li/ul/li//*[text()='{save_dir}']"
            )
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(random.uniform(1, 3))

            selector = self.driver.find_element_by_xpath("//a[@title='确定']")
            self.driver.execute_script('arguments[0].click()', selector)

            time.sleep(random.uniform(1, 3))

            if '已为您成功保存文件' in self.driver.page_source:
                if verbose:
                    print('success to save')
        except Exception as e:
            print(e)

    def close(self):
        self.driver.close()

    def make_dir(self, dir_name):
        selector = self.dir_exist(dir_name)
        if not selector:
            # 新建按钮
            selector = self.driver.find_element_by_xpath("//a[@title='新建文件夹']")
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(random.uniform(0.5, 1))
            # 输入文件夹名称
            self.driver.find_element_by_class_name('GadHyA').send_keys(dir_name)
            time.sleep(random.uniform(0.5, 1))
            selector = self.driver.find_element_by_class_name('gwtz8xMb')
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(random.uniform(0.5, 1))

    def dir_exist(self, dir_name):
        selector = None
        try:
            selector = self.driver.find_element_by_xpath(
                f"//div[@class='vdAfKMb']/dd/div[@class='file-name']//div[@class='text']//*[text()='{dir_name}']"
            )
        except NoSuchElementException:
            pass
        return selector

    def dir_list(self):
        dir_names = None
        try:
            dir_names = [
                element.text for element in self.driver.find_elements_by_xpath(
                    "//div[@class='vdAfKMb']/dd/div[@class='file-name']"
                )]
        except NoSuchElementException:
            pass
        if dir_names:
            print('全部文件 -->')
            for dir_name in dir_names:
                print(f'\t{dir_name}')

    def locate_dir(self, dir_name):
        selector = self.dir_exist(dir_name)
        if selector:
            self.driver.execute_script('arguments[0].click()', selector)
            time.sleep(random.uniform(0.5, 1))
    
    def make_path(self, path):
        dir_names = path.split('/')
        for step in range(len(dir_names)):
            self.make_dir(dir_names[step])
            if step < len(dir_names):
                self.locate_dir(dir_names[step])

    def known(self):
        try:
            selector = self.driver.find_element_by_class_name('know-button')
            self.driver.execute_script('arguments[0].click()', selector)
        except NoSuchElementException:
            pass


if __name__ == '__main__':

    """
    # get cookie
    cd = CloudDisk()
    cd.manual_login()
    # login manually and save
    cd.save_cookie(cookie_path='cookie/drive_cookie.txt')
    """

    """
    # 操作文件夹
    cd = CloudDisk(headless=False, limit=False, maximize=False, delete_cookies=False)
    cd.login_with_cookie(cookie_path='cookie/drive_cookie.txt')
    cd.known()
    cd.dir_list()
    cd.make_dir('test')
    cd.dir_exist('test')
    cd.make_path('test/test1/test2/test3')
    """

    cd = CloudDisk()
    cd.login_with_cookie(cookie_path='cookie/drive_cookie.txt')

    items = [
        ('https://pan.baidu.com/s/1NxtrD9QbONy0xRxqXut5Bw', '8irj'),
        ('https://pan.baidu.com/s/1YJw9auKFnKMSeJaYb1PJTg', 'mqxz'),
        ('https://pan.baidu.com/s/17YYdXFyHjVAvbka0J2BFug', 'f8aa'),
        ('https://pan.baidu.com/s/1010Vnz9YZq6ygcsawKqiPw', 'fw38'),
        ('https://pan.baidu.com/s/1T4Chc6h14NOWLPSQI7VVQw', '7tuk'),
        ('https://pan.baidu.com/s/1tvDg7beobRmmFgtLP0zgXQ', 'a9z2'),
        ('https://pan.baidu.com/s/11-cMUa52HGoP_B13yDKhCw', 'p7da'),
    ]

    for item in items:
        cd.save(url=item[0], pwd=item[1], save_dir='test')
