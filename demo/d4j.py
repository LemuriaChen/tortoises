

from tortoises.driver import start_chrome

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
import time
# import re


start = time.time()

base_url = 'https://www.d4j.cn'
driver = start_chrome(headless=True)

tags = ['小说文学', '畅销图书', '合集套装', '学习干货', ]
url_tags = ['xiaoshuowenxue', 'changxiao-tushu', 'hejitaozhuang', 'xuexi-ganhuo']
tag_pages = [153, 23, 92, 13]


"""
# 登陆百度网盘主页
driver.get('https://pan.baidu.com/')
WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
    expected_conditions.presence_of_element_located((By.XPATH, "//div")))
time.sleep(2)

# 更改登陆方式
driver.find_element_by_class_name('tang-pass-footerBarULogin').click()
time.sleep(2)

# 输入用户名和密码
driver.find_element_by_id("TANGRAM__PSP_4__userName").send_keys('15071320287')
driver.find_element_by_id("TANGRAM__PSP_4__password").send_keys('chenwei1993')
driver.find_element_by_id("TANGRAM__PSP_4__submit").click()
time.sleep(5)
"""


for part in range(len(tags)):

    tag = tags[part]
    url_tag = url_tags[part]
    pages = tag_pages[part]
    print(f'正在抓取 < {tag} > ...')

    for page in range(1, pages + 1):

        # 登陆主页
        url = f'{base_url}/book/{url_tag}/page/{page}'
        print(f'正在抓取 < {tag} > 第 < {page} > 页 -> {url}')
        try:
            driver.get(url)
            WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div")))
        except Exception as e:
            print(f'< {tag} > 第 < {page} > 页抓取失败，跳过！\n{e}')
            continue

        time.sleep(2)
        print(f'< {tag} > 第 < {page} > 页抓取成功！')

        # 解析链接
        try:
            hrefs = [element.get_attribute('href') for element in driver.find_elements_by_xpath(
                "//article//h2[@class='kratos-entry-title-new']//a")]
        except Exception as e:
            print(f'解析 < {tag} > 第 < {page} > 页失败，跳过！\n{e}')
            continue

        if hrefs:
            print(f'解析 < {tag} > 第 < {page} > 页，共 < {len(hrefs)} > 个链接')

            for href in hrefs:
                # 具体链接
                print('=' * 50)
                try:
                    print(f'当前链接：{href}')
                    driver.get(href)
                    WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
                        expected_conditions.presence_of_element_located((By.XPATH, "//div")))
                except Exception as e:
                    print(e)
                    continue

                time.sleep(2)

                # if '提取码' not in driver.page_source:
                try:
                    extra_link = driver.find_element_by_class_name('downbtn').get_attribute('href')
                    print(f'跳转链接：{extra_link}')
                    driver.get(extra_link)
                    WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
                        expected_conditions.presence_of_element_located((By.XPATH, "//div")))
                except Exception as e:
                    print(e)
                    continue

                time.sleep(2)

                vc = ''
                for element in driver.find_elements_by_xpath("//div[@class='plus_l']//li"):
                    if '百度网盘提取码 ：' in element.text:
                        vc = element.text.replace('百度网盘提取码 ：', '').strip()

                drive_url = driver.find_element_by_xpath("//div[@class='panel-body']/span/a").get_attribute('href')

                # else:
                #     vc = re.findall('提取码: ([a-zA-Z0-9]{4})', driver.page_source)[0]
                #     drive_url = driver.find_element_by_class_name('downbtn').get_attribute('href')

                if vc:
                    print(f'百度网盘链接: {drive_url}, 验证码: {vc}')

                    with open('link.txt', 'a+') as f:
                        f.write(drive_url + ',' + vc + '\n')

                """
                try:
                    driver.get(drive_url)
                    WebDriverWait(driver=driver, timeout=60, poll_frequency=0.5).until(
                        expected_conditions.presence_of_element_located((By.XPATH, "//div")))
                except Exception as e:
                    print(e)
                    continue

                time.sleep(2)

                try:
                    driver.find_element_by_xpath('//input').send_keys(vc)
                    driver.find_element_by_class_name('g-button-right').click()
                except NoSuchElementException:
                    pass

                try:
                    # 全部选中
                    driver.find_element_by_class_name('Qxyfvg').click()
                    # 保存到网盘
                    driver.find_element_by_class_name('g-button').click()
                except Exception as e:
                    print(e)

                try:
                    for element in driver.find_elements_by_xpath("//div[@class='file-tree-container']//ul/li"):
                        if element.text.startswith('电子书资源'):
                            element.click()
                            break
                    driver.find_element_by_xpath("//a[@title='确定']").click()
                    time.sleep(2)
                    print('成功保存至网盘！')
                except Exception as e:
                    print(e)
                """

driver.close()

end = time.time()
print(f'done! {round(end - start, 4)} seconds used.')

