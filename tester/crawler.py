import csv
import logging

from bs4 import BeautifulSoup
from collections import deque
from pyvirtualdisplay import Display
from selenium import webdriver
from urllib.parse import urldefrag, urljoin

from exceptions import ImproperlyConfigured 


class Crawler(object):
    """
    A Crawler that finds documents that have certain 
    characteristics.
    """

    def __init__(self, db, base_url=None, start_url=None, levels=1):
        """Setup and validate arguments to make them available 
        
        Arguments:
            db  -- MongoDB connection
        
        Keyword Arguments:
            start_url {str} -- URL (default: {None})
            base_url {str} -- URL (default: {None})
            levels {int} -- Number of levels to crawl (default: {1})
        """

        if not db:
            raise(ImproperlyConfigured('database connection'))
        elif not start_url:
            raise(ImproperlyConfigured('start url'))
        elif not base_url:
            raise(ImproperlyConfigured('base url'))
        elif not int(levels):
            raise(ValueError(int))

        # Fake display for selenium
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # Add path to your Firefox.
        self.browser = webdriver.Firefox(log_path='/var/log/geckolog.log')
        # The start might change after the setup method 
        self.start = start_url
        self._setup()

    def _setup(self):
        """
        Method dedicated to take care of authentication
        and general setup to start the crawling
        """
        pass
    
    def get_page(self, url):
        try:
            self.browser.get(url)
            return self.browser.page_source
        except Exception as e:
            logging.exception(e)
            return

    def get_soup(self, html):
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return
    
    def get_links(self, soup):
        for link in soup.find_all('a', href=True): #All links which have a href element
            link = link['href'] #The actually href element of the link
            url = urljoin(self.base, urldefrag(link)[0]) #Resolve relative links using base and urldefrag
            if url not in self.url_queue and url not in self.crawled_urls: #Check if link is in queue or already crawled
                if url.startswith(self.base): #If the URL belongs to the same domain
                    self.url_queue.append(url) #Add the URL to our queue

    def get_data(self, soup):
        try:
            title = soup.find('title').get_text().strip().replace('\n','')
        except:
            title = None
 
        return title

    def run_crawler(self):
        try:
            while len(self.url_queue): #If we have URLs to crawl - we crawl
                current_url = self.url_queue.popleft() #We grab a URL from the left of the list
                self.crawled_urls.append(current_url) #We then add this URL to our crawled list
                html = self.get_page(current_url) 
                if self.browser.current_url != current_url: #If the end URL is different from requested URL - add URL to crawled list
                    self.crawled_urls.append(current_url)
                soup = self.get_soup(html)
                if soup is not None:  #If we have soup - parse and write to our csv file
                    self.get_links(soup)
                    title = self.get_data(soup)
                    self.csv_output(current_url, title)
        except:
            self.display.stop()
        