
# FuDan University

# 这里写了一些从复旦大学忘道溯源文献搜索系统进行文献检索和下载的基本逻辑。

from tortoises.web.driver import start_chrome

driver = start_chrome(headless=False, limit=False)

url = 'http://discovery.fudan.edu.cn'
driver.get(url)
driver.find_element_by_xpath(
    "//div[@class='EXLSearchFieldRibbonFormFields']"
    "/div[@class='EXLSearchFieldRibbonFormSearchFor']/input"
).send_keys('climate change')

driver.find_element_by_xpath(
    "//div[@class='EXLSearchFieldRibbonFormSubmitSearch']"
    "/input"
).click()


driver.find_elements_by_class_name('EXLResult')
a = driver.find_elements_by_class_name('EXLResult')

# title
a[1].find_element_by_class_name('EXLResultTitle').find_element_by_tag_name('a').text

# click
a[1].find_element_by_class_name('EXLResultTitle').find_element_by_tag_name('a').click()

# author
a[1].find_element_by_class_name('EXLResultAuthor').text

# detail
a[1].find_element_by_class_name('EXLResultDetails').text

# search info
driver.find_element_by_id('resultsNumbersTileBottom').find_element_by_tag_name('em').text
driver.find_element_by_class_name('EXLResultsSortBy').find_element_by_class_name('EXLResultsSortBySelected').click()

# next page
# current page
driver.find_element_by_xpath(
    "//div[@id='resultsNavNoIdBottom']"
    "/span[@class='EXLDisplayedCount EXLBriefResultsPaginationPageCount']"
).text
driver.find_elements_by_link_text('2')


driver.find_element_by_xpath("//a[@title='Navigate to target in new window']").click()

driver.switch_to.window(driver.window_handles[1])

urls = driver.find_elements_by_xpath("//a")
for url in urls:
    # print(url.get_attribute('href'))
    # print(url.text)
    if url.get_attribute('href').endswith('pdf'):
        print(url.get_attribute('href'))
        break


import wget
wget.download(url.get_attribute('href'))

driver.get(url.get_attribute('href'))
wget.download(driver.current_url)









