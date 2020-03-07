
from time import sleep
import random
import re
from collections import defaultdict
import json

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException

from tortoises.driver import start_chrome
from tortoises.util import time


class AppWebKnowledge(object):

    def __init__(self, headless=True, verbose=True, *args):

        self.base_url = 'http://apps.webofknowledge.com'
        self.driver = start_chrome(headless, *args)
        self.base_handle = self.driver.current_window_handle

        self.verbose = verbose
        self.num_items_per_cited_page = 30

        self.search_status = None                       # 搜索结果状态
        self.unique_matched = None                      # 搜索结果
        self.homepage_status = None                     # 文章主页获取状态（如果搜索结果唯一的话）
        self.searched_title = None                      # 搜索的第一条结果（如果搜索结果唯一的话）

        self.num_pages = None
        self.num_items = None
        self.num_items_per_page = None
        self.num_items_current_page = None
        self.current_page = None
        self.num_citing_crawled = None

        # self.ABBR_NAME_EXTRACT_PATTERN = re.compile(r'\(.*?\)|\[.*?\]')
        # self.FULL_NAME_EXTRACT_PATTERN = re.compile(r'\((.*?)\)')
        # self.ORC_ID_EXTRACT_PATTERN = re.compile(r'\d+-\d+-\d+-\d+')
        # self.REPRINT_AUTHOR_EXTRACT_PATTERN = re.compile(r'Reprint Address:(.*?)\(reprint author\)')
        # self.SINGLE_QUOTES_EXTRACT_PATTERN = re.compile(r'\'(.*)\'')
        # self.ADDRESS_PATTERN = re.compile(r'\[.*?\]')
        # self.NUM_PATTERN = re.compile(r'\d')
        # self.YEAR_PATTERN = re.compile(r'\d{4}?')
        #
        # self.CORE_FIELDS = {
        #     'Volume': 'vol', 'Issue': 'issue', 'Pages': 'pages', 'Part': 'part', 'Article Number': 'art_num',
        #     'DOI': 'doi', 'Published': 'date', 'Document Type': 'doc_type', 'Publisher': 'publisher',
        #     'Author Keywords': 'keywords', 'KeyWords Plus': 'keywords_plus', 'E-mail Addresses': 'email',
        #     'Research Areas': 'sc', 'Web of Science Categories': 'category', 'Language': 'language',
        #     'ISSN': 'sn', 'eISSN': 'ei', 'Accession Number': 'ut', 'IDS Number': 'ga', 'PubMed ID': 'pm',
        # }
        # self.OTHER_CORE_FIELDS = {
        #     'journal': 'sourceTitle',
        #     'citing': 'snowplow-citation-network-times-cited-count-link',
        #     'citing_all': 'snowplow-citation-network-all-times-cited',
        #     'cited': 'snowplow-citation-network-cited-reference-count-link',
        # }
        # self.parsed_info = {}

    def init(self):

        self.search_status = None
        self.unique_matched = None
        self.homepage_status = None
        self.searched_title = None

        self.num_pages = None
        self.num_items = None
        self.num_items_per_page = None
        self.num_items_current_page = None
        self.current_page = None
        self.num_citing_crawled = None

    def fetch_home(self):

        # init status
        self.init()

        # step 1. login homepage
        try:
            if self.verbose:
                print(f'[{time()}]:\033[1;36m connecting to\033[0m < http://apps.webofknowledge.com > ...')
            self.driver.get('http://apps.webofknowledge.com')
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//div")))
        except Exception as e:
            if self.verbose:
                print(f'[{time()}]:\033[1;31m fail\033[0m to login < http://apps.webofknowledge.com > .\n{e}')
            return

        print(f'[{time()}]:\033[1;36m success\033[0m to login < http://apps.webofknowledge.com > .')
        sleep(random.uniform(1, 3))

        # step 2. switch web language to english if not
        try:
            self.driver.find_element_by_xpath('//a[@title="English"]')
        except NoSuchElementException:
            for language in ['简体中文', '繁體中文', '日本語', '한국어', 'Português', 'Español', 'Русский']:
                try:
                    self.driver.find_element_by_xpath(f'//a[@title="{language}"]').click()
                    sleep(random.uniform(4, 6))
                    self.driver.find_element_by_xpath('//ul//a[contains(text(), "English")]').click()
                    WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, "search-criteria-input-wr")))
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to switch web language from {language} to English.')
                    sleep(random.uniform(2, 4))
                    break
                except (NoSuchElementException, TimeoutException, ):
                    pass
        return self

    def search(self, argument, mode='title'):

        print(f'[{time()}]:\033[1;36m searching\033[0m < \033[1;33m{argument}\033[0m > by < \033[1;35m{mode}\033[0m > .')

        """
        # step 0. clear history search records
        try:
            self.driver.find_element_by_id(
                'clearIcon1').click()
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to clear history search records .')
            sleep(random.uniform(1, 3))
        except (NoSuchElementException, ElementNotInteractableException,
                ElementClickInterceptedException, ):
            pass
        """

        # step 1. enter searched argument
        try:
            selector = self.driver.find_element_by_xpath(
                "//div[@class='search-criteria-input-wr']/input"
            )
            selector.clear()
            sleep(random.uniform(1, 2))
            selector.send_keys(argument)
            sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to enter article title .')
            sleep(random.uniform(1, 3))
        except NoSuchElementException:
            print(f'[{time()}]:\033[1;31m fail\033[0m to enter article title .')
            return

        # step 2. switch search mode
        try:
            self.switch_search_mode(mode)
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException, ):
            sleep(random.uniform(1, 2))
            # minimize questionnaire column if exits
            self.hide_advertise_widget()
            try:
                self.switch_search_mode(mode)
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f'[{time()}]:\033[1;31m fail\033[0m to switch search mode, may have triggered exceptions .')
                return

        sleep(random.uniform(1, 3))

        # step 3. click search button
        try:
            self.click_search_button()
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
            sleep(random.uniform(1, 2))
            # minimize questionnaire column if exits
            self.hide_advertise_widget()
            try:
                self.click_search_button()
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f'[{time()}]:\033[1;31m fail\033[0m to search articles, may have triggered exceptions .')
                return

        if self.verbose:
            print(f'[{time()}]:\033[1;37m searched ...\033[0m')
        sleep(random.uniform(1, 3))

        # step 4. parse search results
        searched_titles = [item.text.strip() for item in self.driver.find_elements_by_xpath(
            "//div[@class='search-results-content']//a[@class='smallV110 snowplow-full-record']"
        )]

        if len(searched_titles) == 0:
            self.search_status = False
            self.unique_matched = False
            if self.verbose:
                print(f'[{time()}]:\033[1;31m fail\033[0m to parse the searched page .')
                print(f'[{time()}]:\033[1;31m none\033[0m matched result found .')
        elif len(searched_titles) == 1:
            self.search_status = True
            self.unique_matched = True
            self.searched_title = searched_titles[0]
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse the searched page .')
                print(f'[{time()}]:\033[1;36m unique\033[0m matched result found .')
        else:
            self.search_status = True
            self.unique_matched = False
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse the searched page .')
                print(f'[{time()}]:\033[1;33m multiple\033[0m matched results found .')
        sleep(random.uniform(2, 3))

    def search_init(self):

        self.num_pages = self._pages_count()
        self.num_items = self._items_count()
        self.num_items_per_page = self._items_per_page_count()
        self.num_items_per_page = self.num_items_per_page if self.num_items_per_page else self.num_items_per_cited_page
        self.num_items_current_page = self._items_current_page_count()
        self.current_page = 1
        self.num_citing_crawled = 0

        print(f'[{time()}: < \033[1;34m{ apk.num_items }\033[0m > searched items with < \033[1;34m{ apk.num_pages }'
              f'\033[0m > pages and < \033[1;34m{ apk.num_items_per_page }\033[0m > terms per page .')

        if self.num_pages * self.num_items_per_page < self.num_items:
            print(f'[{time()}: <\033[1;36m pages \033[0m> may\033[1;32m be truncated\033[0m .')

    def switch_search_mode(self, mode):
        """
        :param mode: 'topic','title','author','doi'
        """
        selector = self.driver.find_element_by_id('select2-select1-container')
        current_mode = selector.text.lower()

        if current_mode != mode:
            selector.click()
            sleep(random.uniform(2, 4))
            selectors = self.driver.find_elements_by_class_name('select2-results__option')
            for selector in selectors:
                if selector.text.lower() == mode:
                    selector.click()
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to change search mode '
                              f'from < by {current_mode} > to < by {mode} > .')
                    sleep(random.uniform(2, 4))
                    break

    def hide_advertise_widget(self):
        try:
            self.driver.find_element_by_xpath(
                '//span[contains(@class, "widget")]'
            ).click()
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to minimize advertising widget .')
            sleep(random.uniform(2, 4))
        except NoSuchElementException:
            pass

    def click_search_button(self):
        self.driver.find_element_by_class_name(
            'searchButton').click()
        WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div")))

    def fetch_article(self, argument, mode='title'):
        """
        :param argument: search query
        :param mode: search mode
        :return: login the article homepage,
                 the article should be exist and unique, using mode < doi > can be a guarantee .
        """
        # fetch_home and search
        self.fetch_home().search(argument=argument, mode=mode)

        # fetch homepage
        if self.search_status and self.unique_matched:
            # login the article homepage if the searched result is exist and unique
            try:
                url = self.driver.find_element_by_class_name(
                    'search-results-item'
                ).find_element_by_class_name('snowplow-full-record').get_attribute('href')
                # do not open a new window
                self.driver.get(url)
                WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                    expected_conditions.presence_of_element_located((By.XPATH, "//div")))
                sleep(random.uniform(2, 4))
                # even if there is no error reported here,
                # it is not necessarily successful to log in to the homepage of the article.
                # it's need to see if there is a < title > class element.
                if self.driver.find_elements_by_class_name('title'):
                    self.homepage_status = True
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to login homepage of article .')
                    sleep(random.uniform(1, 3))
            except (NoSuchElementException, TimeoutException, ):
                if self.verbose:
                    print(f'[{time()}]:\033[1;31m fail\033[0m to login homepage of article .')
        else:
            if self.verbose:
                print(f'[{time()}]:\033[1;34m do not\033[0m login homepage of article .\n\tplease check '
                      f'<\033[1;34m self.search_status\033[0m > and <\033[1;34m self.unique_matched\033[0m > .')

    # def parse_article(self, **kwargs):
    #
    #     # search more authors if exits
    #     try:
    #         self.driver.find_element_by_id(
    #             'show_more_authors_authors_txt_label').click()
    #         sleep(random.uniform(1, 2))
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to find more authors .')
    #     except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, ):
    #         pass
    #
    #     # search ResearcherID and ORC-ID if exits
    #     try:
    #         self.driver.find_element_by_id(
    #             'show_resc_blurb_link').click()
    #         sleep(random.uniform(1, 2))
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to find Researcher-ID and ORC-ID .')
    #     except (NoSuchElementException, ElementNotInteractableException,
    #             ElementClickInterceptedException):
    #         pass
    #
    #     # search funding text information if exits
    #     try:
    #         selector = self.driver.find_element_by_id(
    #             'show_fund_blurb_link')
    #         # if 'none' in selector.get_attribute('style'):
    #         selector.click()
    #         sleep(random.uniform(1, 2))
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to find out funding text .')
    #     except (NoSuchElementException, ElementNotInteractableException,
    #             ElementClickInterceptedException,):
    #         pass
    #
    #     # search more data fields
    #     try:
    #         selector = self.driver.find_element_by_id(
    #             'hidden_section_label')
    #         if re.findall(r'see more', selector.text.lower()):
    #             self.driver.execute_script("arguments[0].click();", selector)
    #             sleep(random.uniform(1, 2))
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to find out more data fields .')
    #     except Exception as e:
    #         print(e)
    #
    #     # parse core fields
    #     try:
    #         for element in self.driver.find_elements_by_class_name('FR_field'):
    #             value = element.text.strip()
    #             for field in self.CORE_FIELDS:
    #                 if value.startswith(field):
    #                     if ':' in value:
    #                         value = ''.join(value.replace(field, '').split(':')[1:]).strip()
    #                     else:
    #                         value = value.replace(field, '').strip()
    #                     self.parsed_info.update({
    #                         self.CORE_FIELDS.get(field): value
    #                     })
    #                     if self.verbose:
    #                         print(f'[{time()}]:\033[1;36m success\033[0m to parse < {field.lower()} > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse other core fields
    #     for field in self.OTHER_CORE_FIELDS:
    #         try:
    #             self.parsed_info.update({
    #                 field: self.driver.find_element_by_class_name(
    #                     self.OTHER_CORE_FIELDS.get(field)).text})
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to parse < {field} > field .')
    #         except NoSuchElementException:
    #             pass
    #
    #     # parse < abstract > field
    #     try:
    #         self.parsed_info.update({
    #             'abstract': self.driver.find_element_by_xpath(
    #                 "//div[text()='Abstract' and @class='title3']/.."
    #             ).find_element_by_tag_name('p').text.strip(),
    #         })
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to parse < abstract > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse < publisher > field
    #     try:
    #         self.parsed_info.update({
    #             'publisher': self.driver.find_element_by_xpath(
    #                 "//div[text()='Publisher' and @class='title3']/.."
    #             ).find_element_by_tag_name('p').text.strip(),
    #         })
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to parse < abstract > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse < funding text > field
    #     try:
    #         self.parsed_info.update({
    #             'funding_text': self.driver.find_element_by_id('show_fund_blurb').text,
    #         })
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to parse < funding text > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse < funding > field
    #     agency, grant_number = [], []
    #     try:
    #         for tb_row in self.driver.find_element_by_xpath(
    #             "//div[text()='Funding' and @class='title3']/.."
    #         ).find_element_by_tag_name('table').find_elements_by_tag_name('tr')[1:]:
    #             agency.append(tb_row.find_elements_by_tag_name('td')[0].text.strip())
    #             grant_number.append(tb_row.find_elements_by_tag_name('td')[1].text.strip())
    #         if agency or grant_number:
    #             self.parsed_info.update({'funding': {'agency': agency, 'grant_number': grant_number}})
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to parse < funding > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse < authors > field
    #     try:
    #         authors = self.driver.find_element_by_xpath(
    #             "//span[contains(text(), 'By') and @class='FR_label']/.."
    #         ).text.replace('By:', '').replace('...Less', '')
    #         abbr_author_names = [author.strip() for author in self.ABBR_NAME_EXTRACT_PATTERN.sub('', authors).split(';')]
    #         full_author_names = [author.strip() for author in self.FULL_NAME_EXTRACT_PATTERN.findall(authors)]
    #         self.parsed_info.update({'abbr_names': abbr_author_names, 'full_names': full_author_names})
    #         if self.verbose:
    #             print(f'[{time()}]:\033[1;36m success\033[0m to parse '
    #                   f'<\033[1;36m {len(abbr_author_names)}\033[0m > abbreviated author names and '
    #                   f'<\033[1;36m {len(full_author_names)}\033[0m > full author names .')
    #         assert len(abbr_author_names) == len(full_author_names)
    #     except NoSuchElementException:
    #         pass
    #     except AssertionError:
    #         print(f'[{time()}]:\033[1;31m inconsistent\033[0m number of authors .')
    #
    #     # parse < reprint authors> field
    #     try:
    #         self.parsed_info['reprint_authors'] = list(set([_.strip() for _ in self.REPRINT_AUTHOR_EXTRACT_PATTERN.findall(
    #             self.driver.find_element_by_xpath(
    #                 "//div[@class='title3' and contains(text(), 'Author Information')]/parent::*[1]").text)]))
    #         if self.verbose:
    #             print(f"[{time()}]:\033[1;36m success\033[0m to parse <\033[1;36m "
    #                   f"{len(self.parsed_info['reprint_authors'])}\033[0m > reprint authors .")
    #     except NoSuchElementException:
    #         pass
    #
    #     # parse < author addresses > field
    #     if self.parsed_info.get('abbr_names') and self.parsed_info.get('full_names'):
    #         addresses = {}
    #         try:
    #             for element in self.driver.find_elements_by_xpath(
    #                     "//table[@class='FR_table_noborders']//td[@class='fr_address_row2']"):
    #                 try:
    #                     addresses.update({
    #                         element.find_element_by_tag_name('a').get_attribute('name').strip():
    #                             self.ADDRESS_PATTERN.sub('', element.find_element_by_tag_name('a').text).strip()
    #                     })
    #                 except (NoSuchElementException, AttributeError, ):
    #                     pass
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to parse <\033[1;36m {len(addresses)}\033[0m > addresses .')
    #         except NoSuchElementException:
    #             pass
    #
    #         if addresses:
    #             author_addresses_list = []
    #             reprint_author_addresses = defaultdict(list)
    #             try:
    #                 for sup in self.driver.find_element_by_xpath(
    #                         "//span[text()='By:' and @class='FR_label']/..").find_elements_by_tag_name('sup'):
    #                     abbr_name = sup.find_element_by_xpath('preceding-sibling::*[1]').text.strip()
    #                     for a in sup.find_elements_by_tag_name('a'):
    #                         address = addresses.get(self.SINGLE_QUOTES_EXTRACT_PATTERN.findall(a.get_attribute('href'))[0])
    #                         author_addresses_list.append(
    #                             [abbr_name, address]
    #                         )
    #                         if self.parsed_info.get('reprint_authors') and abbr_name in self.parsed_info.get('reprint_authors'):
    #                             reprint_author_addresses[abbr_name].append(address)
    #                 author_addresses = defaultdict(list)
    #                 for author, address in author_addresses_list:
    #                     author_addresses[address].append(author)
    #                 self.parsed_info.update({
    #                     'author_addresses': author_addresses,
    #                     'reprint_author_addresses': reprint_author_addresses
    #                 })
    #                 if self.verbose:
    #                     print(f'[{time()}]:\033[1;36m success\033[0m to parse author addresses and '
    #                           f'<\033[1;36m {len(reprint_author_addresses)}\033[0m > reprint authors addresses .')
    #             except NoSuchElementException:
    #                 pass
    #
    #     # parse < ORC-ID > field
    #     orc_ids = {}
    #     try:
    #         for tb_row in self.driver.find_element_by_id(
    #                 'show_resc_blurb').find_element_by_tag_name('table').find_elements_by_tag_name('tr')[1:]:
    #             td_col = tb_row.find_elements_by_tag_name('td')
    #             orc_id = td_col[2].text.strip().replace('http://orcid.org/', '').strip()
    #             author = td_col[0].text
    #             orc_ids[orc_id] = author
    #         if orc_ids:
    #             self.parsed_info.update({'orc_ids': orc_ids})
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to parse < orc-id > field .')
    #     except NoSuchElementException:
    #         pass
    #
    #     if self.verbose:
    #         print(f'[{time()}]:\033[1;32m success\033[0m to parse the whole html DOM tree of the article .')
    #
    #     # process numerical field
    #     for key in ['citing_all', 'citing', 'cited', ]:
    #         if key not in self.parsed_info or not self.parsed_info.get(key):
    #             self.parsed_info[key] = '0'
    #         try:
    #             self.parsed_info[key] = eval(''.join(self.NUM_PATTERN.findall(self.parsed_info[key])))
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to numeric < {key} > field .')
    #         except (NameError, SyntaxError, ):
    #             self.parsed_info[key] = 0
    #
    #     # process < reprint_author, accession number > field
    #     if self.parsed_info.get('reprint_author'):
    #         self.parsed_info['reprint_author'] = self.parsed_info['reprint_author'].replace('(reprint author)', '').strip()
    #     if self.parsed_info.get('ut'):
    #         self.parsed_info['ut'] = self.parsed_info['ut'].replace('WOS', '').strip()
    #
    #     # infer < year > field
    #     if self.parsed_info.get('date'):
    #         try:
    #             self.parsed_info['year'] = eval(self.YEAR_PATTERN.findall(self.parsed_info.get('date'))[0])
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to inference < year > field .')
    #         except (SyntaxError, NameError, IndexError):
    #             pass
    #
    #     # dumps some fields
    #     for field in ['abbr_names', 'full_names', 'reprint_authors', 'author_addresses', 'funding', ]:
    #         if field in self.parsed_info:
    #             self.parsed_info[field] = json.dumps(self.parsed_info[field])
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to dumps the < {field} > field .')
    #
    #     # dumps some fields
    #     journal_detail = {}
    #     for field in ['vol', 'issue', 'pages', 'part', 'art_num', ]:
    #         if field in self.parsed_info:
    #             journal_detail[field] = self.parsed_info.get(field)
    #             if self.verbose:
    #                 print(f'[{time()}]:\033[1;36m success\033[0m to dumps the < {field} > field .')
    #     if journal_detail:
    #         self.parsed_info['journal_detail'] = json.dumps(journal_detail)
    #
    #     # add additional fields if exits
    #     self.parsed_info.update(kwargs)
    #
    #     if self.verbose:
    #         print(f'[{time()}]:\033[1;32m success\033[0m to process and clean the article fields .')

    def sort(self, key='date', reverse=False):
        """
        :param key: sort key, should be in ['date', 'cited', ]
        :param reverse: sort from high to low by default
        """
        # status is 'times cited' or 'date'
        selector = self.driver.find_element_by_class_name('sorttype-sub-nav_list-item-active')
        is_reversed = False if 'down' in selector.find_element_by_class_name('fas').get_attribute('class') else True
        active_type = selector.text.strip().lower()

        if key == 'date':
            if active_type == 'date':
                if reverse != is_reversed:
                    click_times = 1
                else:
                    click_times = 0
            else:
                if reverse:
                    click_times = 2
                else:
                    click_times = 1

            for _ in range(click_times):
                self.driver.find_element_by_xpath(
                    "//div[@class='pagingOptions']//li[contains(text(),'Date')]"
                ).click()
                WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "pagingOptions")))
                sleep(random.uniform(2, 4))

        if key == 'cited':
            if active_type == 'times cited':
                if reverse != is_reversed:
                    click_times = 1
                else:
                    click_times = 0
            else:
                if reverse:
                    click_times = 2
                else:
                    click_times = 1

            for _ in range(click_times):
                self.driver.find_element_by_xpath(
                    "//div[@class='pagingOptions']//li[contains(text(),'Times Cited')]"
                ).click()
                WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, "pagingOptions")))
                sleep(random.uniform(2, 4))

    def _pages_count(self):
        try:
            return eval(self.driver.find_element_by_id('pageCount.top').text.strip().replace(',', ''))
        except Exception as e:
            print(e)
            return None

    def _items_per_page_count(self):
        try:
            return eval(re.findall(r"\d+", self.driver.find_element_by_class_name('selection').text)[0])
        except Exception as e:
            print(e)
            return None

    def _items_count(self):
        try:
            return eval(self.driver.find_element_by_id('hitCount.top').text.strip().replace(',', ''))
        except Exception as e:
            print(e)
            return None

    def _items_current_page_count(self):
        try:
            return len(self.driver.find_elements_by_class_name('search-results-item'))
        except Exception as e:
            print(e)
            return None

    def next_page(self, add=1):
        try:
            # enter page number
            selector = self.driver.find_element_by_class_name('goToPageNumber-input')
            # clear input
            selector.clear()
            sleep(random.uniform(1, 2))
            selector.send_keys(self.current_page + add)
            sleep(random.uniform(1, 2))
            # submit page number
            selector.submit()
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "goToPageNumber-input")))
            sleep(random.uniform(4, 6))
            print(f'[{time()}]:\033[1;36m success\033[0m to fetch page '
                  f'<\033[1;36m {self.current_page + add}\033[0m / \033[1;36m{ self.num_pages }\033[0m > .')
        except Exception as e:
            print(f'[{time()}]:\033[1;31m fail\033[0m to fetch page <\033[1;36m '
                  f'{self.current_page + add}\033[0m / \033[1;36m{ self.num_pages }\033[0m > and skip .\n{e}')

        self.current_page = self.current_page + add
        self.num_items_current_page = self._items_current_page_count()

    def previous_page(self):
        self.next_page(add=-1)

    def fetch_current_page(self, index):
        """
        :param index: searched result index
        """
        try:
            element = self.driver.find_elements_by_class_name('search-results-item')[index]
            url = element.find_element_by_class_name('snowplow-full-record').get_attribute('href')
            # open a new window
            self.driver.execute_script(f'window.open("{url}");')
            self.driver.switch_to.window(self.driver.window_handles[1])
            # wait new window
            WebDriverWait(self.driver, 60, 0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, 'title')))
            sleep(random.uniform(1, 2))

            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to fetch article < \033[1;36m{ index + 1 }\033[0m /'
                      f'\033[1;36m { self.num_items_current_page }\033[0m > from page <\033[1;36m { self.current_page }'
                      f'\033[0m / \033[1;36m{ self.num_pages }\033[0m > .')
            self.num_citing_crawled += 1
        except Exception as e:
            if self.verbose:
                print(f'[{time()}]:\033[1;31m fail\033[0m to fetch article < \033[1;36m{ index + 1 }\033[0m /'
                      f'\033[1;36m { self.num_items_current_page }\033[0m > from page <\033[1;36m { self.current_page }'
                      f'\033[0m / \033[1;36m{ self.num_pages }\033[0m > --> and skip .\n{e}')

    def switch_handle(self):

        if self.driver.current_window_handle != self.base_handle:
            try:
                self.driver.close()
                sleep(random.uniform(0.5, 1))
                self.driver.switch_to.window(self.base_handle)
                sleep(random.uniform(0.5, 1))
            except Exception as e:
                print(e)

    def fetch_citation(self, fetch_type='citing'):
        """
        :param fetch_type: ['citing', 'cited', ]
        """
        try:
            if fetch_type == 'citing':
                self.driver.find_element_by_class_name('snowplow-citation-network-times-cited-count-link').click()
            else:
                self.driver.find_element_by_class_name('snowplow-citation-network-cited-reference-count-link').click()
            WebDriverWait(self.driver, 60, 0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "search-results")))
            sleep(random.uniform(4, 6))
            self.search_init()

            print(f'[{time()}]:\033[1;36m success\033[0m to fetch page '
                  f'<\033[1;36m 1\033[0m / \033[1;36m{ self.num_pages }\033[0m > .')
        except Exception as e:
            print(f'[{time()}]:\033[1;31m fail\033[0m to fetch page '
                  f'<\033[1;36m 1\033[0m / \033[1;36m{ self.num_pages }\033[0m > .\n{e}')


if __name__ == '__main__':

    title = 'The ERA-Interim reanalysis: configuration and performance of the data assimilation system'
    apk = AppWebKnowledge(headless=True)
    apk.fetch_article(argument=title, mode='title')
    apk.fetch_citation(fetch_type='citing')

    while True:
        for idx in range(apk.num_items_current_page):
            apk.fetch_current_page(index=idx)
            print(apk.driver.find_element_by_class_name('title').text)
            apk.switch_handle()
        apk.next_page()

    # apk.fetch_article(argument=title, mode='title')
    # apk.fetch_article(argument='10.1111/hic3.12497', mode='doi')
    # apk.fetch_article(argument='Klein, Naomi', mode='author')

    # apk.fetch_home().search(argument='変なもの', mode='title')
    # apk.fetch_home().search(argument='10.1111/hic3.12497', mode='doi')
    # apk.fetch_home().search(argument='Klein, Naomi', mode='author')

    # apk.fetch_home().search(argument='climate change', mode='title')
    # apk.search_init()
    # print(apk.current_page)
    # print(apk.num_pages)
    # print(apk.num_items_per_page)
    # print(apk.num_items)
    # print(apk.num_items_current_page)
    # apk.sort(key='cited', reverse=True)
    # apk.sort(key='cited', reverse=False)
    # apk.sort(key='date', reverse=True)
    # apk.sort(key='date', reverse=False)
    # apk.next_page()
    # apk.fetch_current_page(index=1)
    # apk.switch_handle()
