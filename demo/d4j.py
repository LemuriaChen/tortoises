

from tortoises.driver import start_chrome

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import time


start = time.time()

base_url = 'https://www.d4j.cn'
driver = start_chrome(headless=True)

tags = ['小说文学', '畅销图书', '合集套装', '学习干货', ]
url_tags = ['xiaoshuowenxue', 'changxiao-tushu', 'hejitaozhuang', 'xuexi-ganhuo']
tag_pages = [153, 23, 92, 13]


for part in range(1, len(tags)):

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

                try:
                    vc = ''
                    for element in driver.find_elements_by_xpath("//div[@class='plus_l']//li"):
                        if '百度网盘提取码 ：' in element.text:
                            vc = element.text.replace('百度网盘提取码 ：', '').strip()

                    drive_url = driver.find_element_by_xpath("//div[@class='panel-body']/span/a").get_attribute('href')
                except Exception as e:
                    print(e)
                    continue

                if vc:
                    print(f'百度网盘链接: {drive_url}, 验证码: {vc}')

                    with open('link.txt', 'a+') as f:
                        f.write(drive_url + ',' + vc + '\n')


driver.close()
end = time.time()
print(f'done! {round(end - start, 4)} seconds used.')

