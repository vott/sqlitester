import csv
import queue
import logging
import re

from bs4 import BeautifulSoup
from collections import deque
from pyvirtualdisplay import Display
from selenium import webdriver
from urllib.parse import urldefrag, urljoin

from exceptions import (
    ImproperlyConfigured,
    EmptyWebPage,
)


class Crawler(object):
    """
    A Crawler that finds documents that have certain 
    characteristics.
    """
    allow_external_urls = False

    def __init__(self, db, base_url=None, initial_path=None, levels=1):
        """Setup and validate arguments to make them available 
        
        Arguments:
            db  -- MongoDB connection
        
        Keyword Arguments:
            initial_path {str} -- URL (default: {None})
            base_url {str} -- URL (default: {None})
            levels {int} -- Number of levels to crawl (default: {1})
        """

        if not db:
            raise(ImproperlyConfigured('database connection'))
        elif not initial_path:
            raise(ImproperlyConfigured('initial path'))
        elif not base_url:
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
        regex.match(url)
        return(regex.group())

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
        self.queue.put(_url)

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
            logging.exception(e)
            return

    def _get_page_object(self, html):
        if not html:
            raise(EmptyWebPage)
        return BeautifulSoup(html, 'lxml')
        
    def get_and_process_links(self, page, parent_url):
        links = page.find_all('a', href=True)
        for link in links:
            _url = link['href']
            if(self.is_relative(_url)):
                _url = '{}{}'.format(self.get_base_url(parent_url), _url)
            if _url not in self.visited and _url not in self.broken_urls:
                self.queue.put(_url)
    
    def run(self):
        try:
            parent_url = '' 
            while True:
                _url = self.queue.get()
                html = self.get_page_source(_url)
                if self.browser.current_url != _url:
                    self.visited.add(self.browser.current_url)
                try:
                    page = self._get_page_object(html)
                except:
                    page = None
                    self.broken_urls.add(_url)
                if page is not None:
                    self.get_and_process_links(page, _url)
                
                self.visited.add(_url) 
        except queue.Empty:
            self.display.stop()
            return True
        





        
    # def get_links(self, soup):
    #     for link in soup.find_all('a', href=True): #All links which have a href element
    #         link = link['href'] #The actually href element of the link
    #         url = urljoin(self.base, urldefrag(link)[0]) #Resolve relative links using base and urldefrag
    #         if url not in self.url_queue and url not in self.crawled_urls: #Check if link is in queue or already crawled
    #             if url.startswith(self.base): #If the URL belongs to the same domain
    #                 self.url_queue.append(url) #Add the URL to our queue