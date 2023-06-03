# VERSION: 2.1
# AUTHORS: sa3dany, Alyetama, BurningMop

# LICENSING INFORMATION
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from html.parser import HTMLParser

from helpers import retrieve_url
from novaprinter import prettyPrinter


class one337x(object):
    url = 'https://1337x.to'
    name = '1337x'
    supported_categories = {
        'all': None,
        'anime': 'Anime',
        'software': 'Applications',
        'games': 'Games',
        'movies': 'Movies',
        'music': 'Music',
        'tv': 'TV',
    }

    class MyHtmlParser(HTMLParser):

        def error(self, message):
            pass

        A, TD, TR, HREF, TABLE = ('a', 'td', 'tr', 'href', 'tbody')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.row = {}
            self.column = None
            self.insideRow = False
            self.foundTable = False
            self.foundResults = False
            self.parser_class = {
                # key: className
                'name': 'name',
                'seeds': 'seeds',
                'leech': 'leeches',
                'size': 'size'
            }

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if 'search-page' in params.get('class', ''):
                self.foundResults = True
                return

            if self.foundResults and tag == self.TABLE:
                self.foundTable = True
                return

            if self.foundTable and tag == self.TR:
                self.insideRow = True
                return

            if self.insideRow and tag == self.TD:
                classList = params.get('class', None)
                for columnName, classValue in self.parser_class.items():
                    if classValue in classList:
                        self.column = columnName
                        self.row[self.column] = -1
                return

            if self.insideRow and tag == self.A:
                if self.column != 'name' or self.HREF not in params:
                    return
                link = params[self.HREF]
                if link.startswith('/torrent/'):
                    link = f'{self.url}{link}'

                    torrent_page = retrieve_url(link)
                    magnet_regex = r'href="magnet:.*"'
                    matches = re.finditer(magnet_regex, torrent_page,
                                          re.MULTILINE)
                    magnet_urls = [x.group() for x in matches]

                    self.row['link'] = magnet_urls[0].split('"')[1]
                    self.row['engine_url'] = self.url
                    self.row['desc_link'] = link

        def handle_data(self, data):
            if self.insideRow and self.column:
                self.row[self.column] = data
                self.column = None

        def handle_endtag(self, tag):
            if tag == 'table':
                self.foundTable = False

            if self.insideRow and tag == self.TR:
                self.insideRow = False
                self.column = None
                array_length = len(self.row)
                if array_length < 1:
                    return
                prettyPrinter(self.row)
                self.row = {}

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        lastli = '<li class="last">'
        category = self.supported_categories[cat]

        if category:
            page_url = f'{self.url}/category-search/{what}/{category}/'
        else:
            page_url = f'{self.url}/search/{what}/'

        # try to get 15 pages (20 * 15 = 300 results) and stop when we don't found results
        results_list = []
        parser = self.MyHtmlParser(self.url)
        page = 1
        while page < 16:
            # download the page
            html = retrieve_url(page_url + str(page) + '/')
            parser.feed(html)
            if html.find(lastli) == -1:
                break
            page += 1
        parser.close()
