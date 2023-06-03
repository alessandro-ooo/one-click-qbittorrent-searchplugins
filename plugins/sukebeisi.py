# -*- coding: utf-8 -*-
#VERSION: 1.11
#AUTHORS: Joost Bremmer (toost.b@gmail.com), vt-idiot
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

# import qBT modules
try:
    from novaprinter import prettyPrinter
    from helpers import retrieve_url
except:
    pass

class sukebeisi(object):
    """Class used by qBittorrent to search for torrents"""

    url = 'https://sukebei.nyaa.si'
    name = 'Sukebei (Nyaa)'
    # defines which search categories are supported by this search engine
    # and their corresponding id. Possible categories are:
    # 'all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books'
    # Anime     = sukebei.nyaa's "Art - Anime"
    # Books     = sukebei.nyaa's "Art - Doujinshi"
    # Games     = sukebei.nyaa's "Art - Games"
    # Pictures  = sukebei.nyaa's "Real Life - Photobooks and Pictures"
    # Movies    = sukbei.nyaa's "Real Life - Videos"
    # If you wish to enable other categories by editing this list or by using one of the unused supported categories (music, software) they are:
    # Top level "Art" category = '1_0'
    # Top level "Real Life" category = '2_0'
    # "Art - Manga" and "Art - Pictures" are included as commented examples below.
    # Simply replace line 53 or 55 with the examples below
    #   'books': '1_4',
    #   'pictures': '1_5',
    supported_categories = {
            'all': '0_0',
            'anime': '1_1',
            'books': '1_2',
            'games': '1_3',
            'pictures': '2_1',
            'movies': '2_2'}

    class SukebeiSiParser(HTMLParser):
        """ Parses sukebei.nyaa.si browse page for search results and prints them"""
        def __init__(self, res, url):
            try:
                super().__init__()
            except:
                #  See: http://stackoverflow.com/questions/9698614/
                HTMLParser.__init__(self)

            self.engine_url = url
            self.results = res
            self.curr = None
            self.td_counter = -1

        def handle_starttag(self, tag, attr):
            """Tell the parser what to do with which tags"""
            if tag == 'a':
                self.start_a(attr)

        def handle_endtag(self, tag):
            if tag == 'td':
                self.start_td()

        def start_a(self, attr):
            params = dict(attr)
            # get torrent name
            if 'title' in params and 'class' not in params and params['href'].startswith('/view/'):
                hit = {
                        'name': params['title'],
                        'desc_link': self.engine_url + params['href']}
                if not self.curr:
                    hit['engine_url'] = self.engine_url
                    self.curr = hit
            elif 'href' in params and params['href'].startswith("magnet:?"):
                if self.curr:
                    self.curr['link'] = params['href']
                    self.td_counter += 1

        def start_td(self):
            # Keep track of timers
            if self.td_counter >= 0:
                self.td_counter += 1

            # Add the hit to the results,
            # then reset the counters for the next result
            if self.td_counter >= 5:
                self.results.append(self.curr)
                self.curr = None
                self.td_counter = -1

        def handle_data(self, data):
            # These fields matter
            if self.td_counter > 0 and self.td_counter <= 5:
                # Catch the size
                if self.td_counter == 1:
                    self.curr['size'] = data.strip()
                # Catch the seeds
                elif self.td_counter == 3:
                    try:
                        self.curr['seeds'] = int(data.strip())
                    except:
                        self.curr['seeds'] = -1
                # Catch the leechers
                elif self.td_counter == 4:
                    try:
                        self.curr['leech'] = int(data.strip())
                    except:
                        self.curr['leech'] = -1
                # The rest is not supported by prettyPrinter
                else:
                    pass

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        """
        Retreive and parse engine search results by category and query.

        Parameters:
        :param what: a string with the search tokens, already escaped
                     (e.g. "Ubuntu+Linux")
        :param cat:  the name of a search category, see supported_categories.
        """

        url = str("{0}/?f=0&s=seeders&o=desc&c={1}&q={2}"
                  .format(self.url,
                          self.supported_categories.get(cat),
                          what))

        hits = []
        page = 1
        parser = self.SukebeiSiParser(hits, self.url)
        while True:
            res = retrieve_url(url + "&p={}".format(page))
            parser.feed(res)
            for each in hits:
                prettyPrinter(each)

            if len(hits) < 75:
                break
            del hits[:]
            page += 1

        parser.close()
