from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib2
#import googlesearch


class GoogleSearchLimitError(Exception):
    pass

class DidNotFindError(Exception):
    pass

class Scraper(object):

    base_url = ""
    search_url = ""

    def construct_search_url(self, query):
        if self.search_url == "":
            msg = "Search url format for site not provided in class definition"
            raise ValueError(msg)
        # need more encoding here
        encoded_query = query.lower().replace(" ","%20")
        return self.search_url % encoded_query

    def connect(self, url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        return soup

    def search(self, query):
        url = self.construct_search_url(query)
        return self.connect(url)

    # def google_search(self, query):
    #     source = urlparse(self.base_url).netloc
    #     google_query = "%s: %s" % (source, query)
    #     try:
    #         url = googlesearch.GoogleSearch(google_query).top_unescaped_url()
    #     except googlesearch.TooManySearchesError:
    #         raise GoogleSearchLimitError
    #     else:
    #         return self.connect(url)

