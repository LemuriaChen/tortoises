
from tortoises.mul_thread import ProcessWrapper
from tortoises.driver import start_chrome
import time
import string


def fun(query):
    driver = start_chrome()
    driver.get(f'https://www.baidu.com/s?wd={query}')
    time.sleep(2)
    driver.close()


query_list = list(string.ascii_lowercase)[:10]
pw = ProcessWrapper(func=fun, tasks=query_list, num_workers=4)

pw.run()
