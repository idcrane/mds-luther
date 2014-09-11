import sys
import re
import urllib2
import scraper
from bs4 import BeautifulSoup
import dateutil.parser
import urlparse
import numpy as np

class BOMojoScraper(scraper.Scraper):

    base_url = "http://www.boxofficemojo.com/"
    search_url = base_url + "search/?q=%s"

    def full_movie_dict_from_title(self,movie_name):
        return self.parse_full_mojo_page(self.get_full_page_url_from_title(movie_name))

    def get_full_page_url_from_title(self,movie_name):
        search_soup = self.search(movie_name)
        found_matches = search_soup.find(text=re.compile("Movie Matches"))
        if found_matches:
            matches_table = found_matches.parent.find_next_sibling("table")
            result_row = matches_table.find_all('tr')[1]
            full_page_url = urlparse.urljoin(self.base_url,result_row.find('a')['href'])

            return full_page_url

        # if we end up here without returning anything, we did not hit a match
        log_message = "[LOG: No match found for %s]" % movie_name
        print >> sys.stderr, log_message
        return -1


    def parse_full_mojo_page(self,full_page_url):
        soup = self.connect(full_page_url)

        release_date = self.to_date(
            self.get_movie_value(soup,'Release Date'))
        domestic_total_gross_string = self.get_movie_value(soup, 'Domestic Total Gross')
        try:
            domestic_total_gross = self.money_to_int(domestic_total_gross_string)
        except AttributeError:
            domestic_total_gross_string = self.deal_with_gross_total_problems(soup)
            domestic_total_gross = self.money_to_int(domestic_total_gross_string)

        runtime = self.runtime_to_minutes(self.get_movie_value(soup,'Runtime'))
        director = self.get_movie_value(soup,'Director')
        rating = self.get_movie_value(soup,'MPAA Rating')

        movie_dict = {
            'movie_title':self.get_movie_title(soup),
            'release_date':release_date,
            'domestic_total_gross':domestic_total_gross,
            'runtime':runtime,
            'director':director,
            'rating':rating
        }

        return movie_dict


    def get_movie_value(self,soup,value_name):
        '''
        takes a string attribute of a movie on the page and
        returns the string in the next sibling object (the value for that attribute)
        '''
        obj = soup.find(text=re.compile(value_name))
        if obj == None:
            return None
        # if obj == None:
        #     return -1
        # else:
        #     return None

        # this works for most of the values
        next_sibling = obj.findNextSibling()
        if next_sibling:
            return next_sibling.text

        # this next part works for the director
        elif obj.find_parent('td'):
            sibling_cell = obj.find_parent('tr').findNextSibling()
            if sibling_cell:
                return sibling_cell.text
                # director_list = []
                # messy_director_list = sibling_cell.find_all(
                        # 'a', href=re.compile('/\?view=Director'))
                # for director in messy_director_list:
                    # director_list.append(director.text)
                # if director_list == []:
                    # director_list = None
                # return director_list

        # this works for movies with estimated totals
        else:
            return -1

    def deal_with_gross_total_problems(self,soup):
        try:
            obj = soup.find(text-re.compile('Estimate'))
            obj = obj.split('(')[0]
            return obj
        except:
            obj = soup.find(text=re.compile('Domestic'))
            obj = obj.find_parent('font').findNextSibling().text
            obj = obj.split('(')[0]
            return obj



    def get_movie_title(self,soup):
        title_tag = soup.find('title')
        movie_title = title_tag.text.split('(')[0].strip()
        return movie_title

    def to_date(self,datestring):
        return dateutil.parser.parse(datestring)

    def money_to_int(self,moneystring):
        return int(moneystring.replace('$','').replace(',',''))



    def runtime_to_minutes(self,runtimestring):
        if runtimestring == 'N/A':
            return np.nan
        rt = runtimestring.split(' ')
        return int(rt[0])*60 + int(rt[2])
