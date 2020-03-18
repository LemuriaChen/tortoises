
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

from tortoises.web.driver import start_chrome
from tortoises.util.help import time


class AppWebKnowledge(object):

    def __init__(self, mode='slow', verbose=True, *args, **kwargs):

        self.base_url = 'http://apps.webofknowledge.com'
        self.mode = mode
        self.verbose = verbose

        self.driver = start_chrome(*args, **kwargs)
        self.base_handle = self.driver.current_window_handle

        self.num_items_per_cited_page = 30
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

        self.AUTHOR_WITH_ADDRESS_PATTERN = re.compile(r'(.*)\((.*)?\)\[(.*)\]')
        self.AUTHOR_WITHOUT_ADDRESS_PATTERN = re.compile(r'(.*)\((.*)?\)')
        self.ADDRESS_PATTERN = re.compile(r'\[(.*?)\](.*)')
        self.YEAR_PATTERN = re.compile(r'\d{4}?')

        self.CORE_FIELDS = {
            'Volume': 'vol',
            'Issue': 'issue',
            'Pages': 'page',
            'DOI': 'doi',
            'Published': 'date',
            'Document Type': 'doc_type',
            'Publisher': 'pub_date',
            'Author Keywords': 'keyword',
            'KeyWords Plus': 'keyword_plus',
            'E-mail Addresses': 'email',
            'Research Areas': 'ra',
            'Web of Science Categories': 'category',
            'Language': 'language',
            'ISSN': 'sn',
            'eISSN': 'ei',
            'Accession Number': 'ut',
            'IDS Number': 'ga',
        }
        self.OTHER_CORE_FIELDS = {
            'journal': 'sourceTitle',
            'citing': 'snowplow-citation-network-times-cited-count-link',
            'citing_all': 'snowplow-citation-network-all-times-cited',
            'cited': 'snowplow-citation-network-cited-reference-count-link',
        }

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
        if self.mode == 'slow':
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
                    if self.mode == 'slow':
                        sleep(random.uniform(2, 4))
                    break
                except (NoSuchElementException, TimeoutException, ):
                    pass

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
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            selector.send_keys(argument)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to enter article title .')
            if self.mode == 'slow':
                sleep(random.uniform(1, 3))
        except NoSuchElementException:
            print(f'[{time()}]:\033[1;31m fail\033[0m to enter article title .')
            return

        # step 2. switch search mode
        try:
            self.switch_search_mode(mode)
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException, ):
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            # minimize questionnaire column if exits
            self.hide_advertise_widget()
            try:
                self.switch_search_mode(mode)
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f'[{time()}]:\033[1;31m fail\033[0m to switch search mode, may have triggered exceptions .')
                return

        if self.mode == 'slow':
            sleep(random.uniform(1, 3))

        # step 3. click search button
        try:
            self.click_search_button()
        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
            if self.mode == 'slow':
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
        if self.mode == 'slow':
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
        if self.mode == 'slow':
            sleep(random.uniform(2, 3))

    def search_init(self):

        self.num_pages = self._pages_count()
        self.num_items = self._items_count()
        self.num_items_per_page = self._items_per_page_count()
        self.num_items_per_page = self.num_items_per_page if self.num_items_per_page else self.num_items_per_cited_page
        self.num_items_current_page = self._items_current_page_count()
        self.current_page = 1
        self.num_citing_crawled = 0

        print(f'[{time()}: < \033[1;34m{ self.num_items }\033[0m > searched articles with '
              f'< \033[1;34m{ self.num_pages }\033[0m > pages and < \033[1;34m{ self.num_items_per_page }\033[0m > '
              f'terms per page .')
        if self.num_pages * self.num_items_per_page < self.num_items:
            print(f'[{time()}: too many <\033[1;36m pages \033[0m> and the response\033[1;32m is truncated\033[0m '
                  f'with a limit <\033[1;34m 10000 \033[0m>.')
        print(f'[{time()}]:\033[1;36m success\033[0m to fetch page '
              f'<\033[1;34m 1\033[0m / \033[1;34m{self.num_pages}\033[0m > .')

    def switch_search_mode(self, mode):
        """
        :param mode: 'topic','title','author','doi'
        """
        selector = self.driver.find_element_by_id('select2-select1-container')
        current_mode = selector.text.lower()

        if current_mode != mode:
            selector.click()
            if self.mode == 'slow':
                sleep(random.uniform(2, 4))
            selectors = self.driver.find_elements_by_class_name('select2-results__option')
            for selector in selectors:
                if selector.text.lower() == mode:
                    selector.click()
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to change search mode '
                              f'from < by {current_mode} > to < by {mode} > .')
                    if self.mode == 'slow':
                        sleep(random.uniform(2, 4))
                    break

    def hide_advertise_widget(self):
        try:
            self.driver.find_element_by_xpath(
                '//span[contains(@class, "widget")]'
            ).click()
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to minimize advertising widget .')
            if self.mode == 'slow':
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
                if self.mode == 'slow':
                    sleep(random.uniform(2, 4))
                # it is not necessarily successful to log in to the homepage of the article
                # even if there is no error reported here
                # therefore it's need to see if there is < title > class element.
                if self.driver.find_elements_by_class_name('title'):
                    self.homepage_status = True
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to login homepage of article .')
                    if self.mode == 'slow':
                        sleep(random.uniform(1, 3))
            except (NoSuchElementException, TimeoutException, ):
                if self.verbose:
                    print(f'[{time()}]:\033[1;31m fail\033[0m to login homepage of article .')
        else:
            if self.verbose:
                print(f'[{time()}]:\033[1;34m do not\033[0m login homepage of article .\n\tplease check '
                      f'<\033[1;34m self.search_status\033[0m > and <\033[1;34m self.unique_matched\033[0m > .')

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
                if self.mode == 'slow':
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
                if self.mode == 'slow':
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
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            selector.send_keys(self.current_page + add)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            # submit page number
            selector.submit()
            WebDriverWait(driver=self.driver, timeout=60, poll_frequency=0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "goToPageNumber-input")))
            if self.mode == 'slow':
                sleep(random.uniform(4, 6))
            print(f'[{time()}]:\033[1;36m success\033[0m to fetch page '
                  f'<\033[1;34m {self.current_page + add}\033[0m / \033[1;34m{ self.num_pages }\033[0m > .')
        except Exception as e:
            print(f'[{time()}]:\033[1;31m fail\033[0m to fetch page <\033[1;34m '
                  f'{self.current_page + add}\033[0m / \033[1;34m{ self.num_pages }\033[0m > and skip .\n{e}')

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
            if self.mode == 'slow':
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
                if self.mode == 'slow':
                    sleep(random.uniform(0.5, 1))
                self.driver.switch_to.window(self.base_handle)
                if self.mode == 'slow':
                    sleep(random.uniform(0.5, 1))
            except Exception as e:
                print(e)

    def fetch_citation(self, _type='citing'):
        """
        :param _type: ['citing', 'cited', ]
        """
        try:
            if _type == 'citing':
                self.driver.find_element_by_class_name('snowplow-citation-network-times-cited-count-link').click()
            else:
                self.driver.find_element_by_class_name('snowplow-citation-network-cited-reference-count-link').click()
            WebDriverWait(self.driver, 60, 0.5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "search-results")))
            if self.mode == 'slow':
                sleep(random.uniform(4, 6))
            self.search_init()

            print(f'[{time()}]:\033[1;36m success\033[0m to fetch page '
                  f'<\033[1;36m 1\033[0m / \033[1;36m{ self.num_pages }\033[0m > .')
        except Exception as e:
            print(f'[{time()}]:\033[1;31m fail\033[0m to fetch page '
                  f'<\033[1;36m 1\033[0m / \033[1;36m{ self.num_pages }\033[0m > .\n{e}')

    def close(self):
        try:
            self.driver.quit()
            print(f'[{time()}]:\033[1;36m success\033[0m to close the chrome driver .')
        except Exception as e:
            print(f'[{time()}]:\033[1;31m fail\033[0m to close the chrome driver .\n{e}')

    def _wrapper(self, element_id, annotation, click_type):
        try:
            selector = self.driver.find_element_by_id(element_id)
            if click_type == 0:
                selector.click()
            else:
                self.driver.execute_script('arguments[0].click()', selector)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to {annotation} .')
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, ):
            return

    def _show_more_authors(self):
        # search more authors if exits
        self._wrapper(
            element_id='show_more_authors_authors_txt_label', annotation='show more authors', click_type=0, )

    def _hide_more_authors(self):
        # search more authors if exits
        self._wrapper(
            element_id='hide_more_authors_authors_txt_label', annotation='hide more authors', click_type=0, )

    def _show_research_id(self):
        # search ResearcherID and ORC-ID if exits
        self._wrapper(element_id='show_resc_blurb_link', annotation='show Researcher-ID and ORC-ID', click_type=0, )

    def _hide_research_id(self):
        # search ResearcherID and ORC-ID if exits
        self._wrapper(element_id='hide_resc_blurb_link', annotation='hide Researcher-ID and ORC-ID', click_type=0, )

    def _show_funding_text(self):
        # search funding text information if exits
        self._wrapper(element_id='show_fund_blurb_link', annotation='show funding text', click_type=0, )

    def _hide_funding_text(self):
        # search funding text information if exits
        self._wrapper(element_id='hide_fund_blurb_link', annotation='hide funding text', click_type=0, )

    def _show_more_fields(self, _type='show'):
        try:
            selector = self.driver.find_element_by_id(
                'hidden_section_label')
            if _type == 'show':
                if re.findall(r'see more', selector.text.lower()):
                    self.driver.execute_script("arguments[0].click();", selector)
                    if self.mode == 'slow':
                        sleep(random.uniform(1, 2))
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to show more data fields .')
            else:
                if re.findall(r'see fewer', selector.text.lower()):
                    self.driver.execute_script("arguments[0].click();", selector)
                    if self.mode == 'slow':
                        sleep(random.uniform(1, 2))
                    if self.verbose:
                        print(f'[{time()}]:\033[1;36m success\033[0m to hide more data fields .')
        except Exception as e:
            print(e)

    def show_journal_impact(self):
        # search journal impact if exits
        try:
            selector = self.driver.find_element_by_class_name('snowplow-JCRoverlay')
            selector.click()
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to show journal impact.')
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, ):
            return

    def hide_journal_impact(self):
        # hide journal impact if exits
        try:
            selector = self.driver.find_element_by_class_name('button4')
            self.driver.execute_script('arguments[0].click()', selector)
            if self.mode == 'slow':
                sleep(random.uniform(1, 2))
            if self.verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to hide journal impact.')
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, ):
            return

    def expand_all_fields(self, funding_text=True):
        self._show_more_authors()
        self._show_research_id()
        if funding_text:
            self._show_funding_text()
        self._show_more_fields(_type='show')

    def fold_all_fields(self):
        self._hide_more_authors()
        self._hide_research_id()
        self._hide_funding_text()
        self._show_more_fields(_type='hide')

    def parse_doi(self, verbose=True):
        # parse < doi > field
        doi = ''
        try:
            doi = self.driver.find_element_by_xpath(
                "//div[@class='block-record-info block-record-info-source']"
                "//span[contains(text(), 'DOI')]/parent::*[1]").text.replace('DOI:', '').strip()
        except NoSuchElementException:
            pass
        if doi and self.verbose and verbose:
            print(f'[{time()}]:\033[1;36m success\033[0m to parse < doi > field .')
        return doi

    def parse_title(self, verbose=True):
        # parse < title > field
        title = ''
        try:
            title = self.driver.find_element_by_class_name('title').text.strip()
        except NoSuchElementException:
            pass
        if title and self.verbose and verbose:
            print(f'[{time()}]:\033[1;36m success\033[0m to parse < title > field .')
        return title

    def parse_abstract(self, verbose=True):
        # parse < abstract > field
        abstract_field = {}
        try:
            abstract = self.driver.find_element_by_xpath(
                "//div[text()='Abstract' and @class='title3']/../p").text
            abstract_field.update({'abstract': abstract})
        except NoSuchElementException:
            pass
        if abstract_field and self.verbose and verbose:
            print(f'[{time()}]:\033[1;36m success\033[0m to parse < abstract > field .')
        return abstract_field

    def parse_core(self, verbose=True):
        # parse < core > fields
        core_field = {}
        try:
            for element in self.driver.find_elements_by_class_name('FR_field'):
                value = element.text.strip()
                for field in self.CORE_FIELDS:
                    if value.startswith(field):
                        if ':' in value:
                            value = ''.join(value.replace(field, '').split(':')[1:]).strip()
                        else:
                            value = value.replace(field, '').strip()
                        core_field.update({
                            self.CORE_FIELDS.get(field): value.replace('WOS', '').strip()
                        })
                        if self.verbose and verbose:
                            print(f'[{time()}]:\033[1;36m success\033[0m to parse < {field.lower()} > field .')
        except NoSuchElementException:
            pass

        # infer < year > field
        if core_field.get('date'):
            try:
                core_field['year'] = eval(self.YEAR_PATTERN.findall(core_field.get('date'))[0])
                if self.verbose and verbose:
                    print(f'[{time()}]:\033[1;36m success\033[0m to inference < year > field .')
            except (SyntaxError, NameError, IndexError):
                pass
        return core_field

    def parse_other_core(self, verbose=True):
        # parse other core fields
        other_core_field = {}
        for field in self.OTHER_CORE_FIELDS:
            try:
                other_core_field.update({
                    field: self.driver.find_element_by_class_name(
                        self.OTHER_CORE_FIELDS.get(field)).text.strip()})
                if self.verbose and verbose:
                    print(f'[{time()}]:\033[1;36m success\033[0m to parse < {field.lower()} > field .')
            except NoSuchElementException:
                pass
        # process numerical field
        for field in ['citing_all', 'citing', 'cited']:
            if field not in other_core_field or not other_core_field.get(field):
                other_core_field[field] = '0'
            try:
                other_core_field[field] = eval(other_core_field.get(field).replace(',', ''))
            except (NameError, SyntaxError):
                other_core_field[field] = 0
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to numeric < {field} > field .')
        return other_core_field

    def parse_author(self, verbose=True):
        # parse < authors > field
        author_field, au, af, addr2af = {}, [], [], defaultdict(list)
        try:
            authors = self.driver.find_element_by_xpath(
                "//p[@class='FR_field']/span[contains(text(), 'By')]/.."
            ).text.replace('By:', '').replace('...Less', '')
            for author in authors.split(';'):
                try:
                    if '[' in author and ']' in author:
                        abbreviated_name, full_name, address_idx = self.AUTHOR_WITH_ADDRESS_PATTERN.findall(author)[0]
                        for addr in address_idx.split(','):
                            addr2af[addr.strip()].append(full_name.strip())
                    else:
                        abbreviated_name, full_name = self.AUTHOR_WITHOUT_ADDRESS_PATTERN.findall(author)[0]
                except IndexError:
                    continue
                au.append(abbreviated_name.strip())
                af.append(full_name.strip())
        except NoSuchElementException:
            pass
        if au and af:
            author_field.update({'au': au, 'af': af})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse <\033[1;36m {len(au)}\033[0m > '
                      f'abbreviated author names and <\033[1;36m {len(af)}\033[0m > full author names with '
                      f'<\033[1;36m {len(addr2af)}\033[0m > addresses .')

        # parse < author addresses > field
        idx2addr = {}
        addresses = self.driver.find_elements_by_xpath(
            "//p[@class='FR_field']/span[contains(text(), 'Addresses')]/../following-sibling::table[1]"
            "/tbody/tr/td[@class='fr_address_row2']/a"
        )
        if addresses:
            for address in addresses:
                try:
                    idx, addr = self.ADDRESS_PATTERN.findall(address.text)[0]
                except IndexError:
                    continue
                idx2addr[idx.strip()] = addr.strip()
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse '
                      f'<\033[1;36m {len(addresses)} \033[0m> addresses .')

        # merge < addresses > field
        c1 = {}
        if idx2addr:
            for idx in idx2addr:
                c1[idx2addr.get(idx)] = addr2af.get(idx) if addr2af.get(idx) else []
            author_field.update({'c1': c1})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < c1 > field .')

        # parse < reprint author> field
        rp = ''
        try:
            rp = self.driver.find_element_by_xpath(
                "//p[@class='FR_field']/span[contains(text(), 'Reprint Address')]/.."
            ).text.replace('Reprint Address:', '').replace('(reprint author)', '').strip()
        except NoSuchElementException:
            pass
        if rp:
            author_field.update({'rp': rp})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse reprint author .')

        return author_field

    def parse_publisher(self, verbose=True):
        # parse < publisher > field
        publisher_field = {}
        try:
            publisher = self.driver.find_element_by_xpath(
                "//div[text()='Publisher' and @class='title3']/../p").text.strip()
            publisher_field.update({'publisher': publisher})
        except NoSuchElementException:
            pass
        if publisher_field:
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < publisher > field .')
        return publisher_field

    def parse_funding(self, verbose=True):
        # parse < funding > field
        funding_field, funding = {}, []
        try:
            for tb_row in self.driver.find_element_by_xpath(
                "//div[text()='Funding' and @class='title3']/.."
            ).find_element_by_tag_name('table').find_elements_by_tag_name('tr')[1:]:
                agency, grant_number = tb_row.find_elements_by_tag_name('td')
                funding.append((agency.text.strip(), grant_number.text.strip()))
        except NoSuchElementException:
            pass
        if funding:
            funding_field.update({'funding': funding})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < funding > field .')

        # parse < funding text > field
        funding_text = ''
        try:
            funding_text = self.driver.find_element_by_id('show_fund_blurb').text.strip()
        except NoSuchElementException:
            pass
        if funding_text:
            funding_field.update({'funding_text': funding_text})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < funding text > field .')

        return funding_field

    def parse_id(self, verbose=True):
        # parse < orc-id > and < researcher-id > field
        id_field, oi, ri = {}, {}, {}
        try:
            for tb_row in self.driver.find_elements_by_xpath(
                    "//div[@class='block-record-info']"
                    "/span[@id='show_resc_blurb']/table/tbody/tr")[1:]:
                author, rid, oid = [_.text.strip().replace(
                    'http://orcid.org/', '').strip() for _ in tb_row.find_elements_by_tag_name('td')]
                if author and rid:
                    ri[rid] = author
                if author and oid:
                    oi[oid] = author
        except NoSuchElementException:
            pass

        if oi:
            id_field.update({'oi': oi})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < orc-id > field .')
        if ri:
            id_field.update({'ri': ri})
            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;36m success\033[0m to parse < researcher-id > field .')

    def parse_article(self, verbose=False, dump=True, **kwargs):

        if not self.parse_title():
            print(f'[{time()}]:\033[1;36m fail\033[0m to parse the article, '
                  f'try to check out the <\033[1;33m validity \033[0m> of current url .')
            return {}
        else:
            parsed_info = {}
            parsed_info.update(self.parse_core(verbose=verbose))
            parsed_info.update(self.parse_other_core(verbose=verbose))
            parsed_info.update(self.parse_author(verbose=verbose))
            parsed_info.update(self.parse_funding(verbose=verbose))
            parsed_info.update(self.parse_abstract(verbose=verbose))
            parsed_info.update(self.parse_publisher(verbose=verbose))

            # dumps some fields
            if dump:
                for field in parsed_info:
                    if isinstance(parsed_info.get(field), list) or isinstance(parsed_info.get(field), dict):
                        parsed_info[field] = json.dumps(parsed_info[field])
                        if self.verbose and verbose:
                            print(f'[{time()}]:\033[1;36m success\033[0m to dumps the < {field} > field .')

            # add additional fields if exits
            parsed_info.update(kwargs)

            if self.verbose and verbose:
                print(f'[{time()}]:\033[1;34m success\033[0m to parse the whole html DOM tree of the article .')
        return parsed_info


if __name__ == '__main__':

    # apk = AppWebKnowledge(mode='slow', verbose=True, headless=False, limit=False, maximize=False)
    #
    # argument = 'The ERA-Interim reanalysis: configuration and performance of the data assimilation system'
    # argument = 'Effects on Carbon Sources and Sinks from Conversion of Over-Mature Forest to ' \
    #            'Major Secondary Forests and Korean Pine Plantation in Northeast China'
    # apk.fetch_article(argument=argument, mode='title')
    # apk.expand_all_fields(funding_text=True)
    # info = apk.parse_article(verbose=True)
    #
    # argument = 'climate change'
    # apk.search(argument=argument, mode='topic')
    pass
