

from tortoises.driver import start_chrome

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import json


driver = start_chrome(headless=False, limit=False)


try:
    print('login...')
    driver.get('https://pan.baidu.com/')
    WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//div")))
    time.sleep(2)
    # # save cookie
    # with open('cookie/drive_cookie.txt', 'w') as f:
    #     f.write(json.dumps(driver.get_cookies()))
except TimeoutException:
    pass


# add cookie
with open('cookie/drive_cookie.txt', 'r') as f:
    print('adding cookie...')
    cookies = json.load(f)
    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        driver.add_cookie(cookie)

driver.refresh()
time.sleep(20)
driver.maximize_window()
time.sleep(5)


items = [
    ('https://pan.baidu.com/s/1NxtrD9QbONy0xRxqXut5Bw', '8irj'),
    ('https://pan.baidu.com/s/1YJw9auKFnKMSeJaYb1PJTg', 'mqxz'),
    ('https://pan.baidu.com/s/17YYdXFyHjVAvbka0J2BFug', 'f8aa'),
    ('https://pan.baidu.com/s/1010Vnz9YZq6ygcsawKqiPw', 'fw38'),
    ('https://pan.baidu.com/s/1T4Chc6h14NOWLPSQI7VVQw', '7tuk'),
    ('https://pan.baidu.com/s/1tvDg7beobRmmFgtLP0zgXQ', 'a9z2'),
    ('https://pan.baidu.com/s/11-cMUa52HGoP_B13yDKhCw', 'p7da'),
]


for url, pwd in items:

    try:

        print(f'百度网盘链接: {url}, 验证码: {pwd}')

        # get url
        driver.get(url)
        WebDriverWait(driver=driver, timeout=100, poll_frequency=0.5).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div")))

        # input password
        driver.find_element_by_xpath('//input').send_keys(pwd)
        # click
        driver.find_element_by_class_name('g-button-right').click()
        WebDriverWait(driver=driver, timeout=100, poll_frequency=0.5).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div[@node-type='fydGNC']")))
        time.sleep(5)

        # select all
        driver.find_element_by_xpath("//div[@node-type='fydGNC']").click()
        time.sleep(5)

        # save
        driver.find_element_by_class_name('g-button').click()
        time.sleep(5)
        WebDriverWait(driver=driver, timeout=100, poll_frequency=0.5).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='file-tree-container']")))

        # optional save path
        driver.find_element_by_xpath(
            "//div[@class='file-tree-container']/ul/li/ul/li//*[text()='电子书资源']"
        ).click()
        time.sleep(10)

        driver.find_element_by_xpath("//a[@title='确定']").click()
        time.sleep(5)

        if '已为您成功保存文件' in driver.page_source:
            print('success to save.')

    except Exception as e:
        print(e)

driver.close()
