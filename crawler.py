from bs4 import BeautifulSoup

import requests

import re


class Crawler:
    '''
    A crawler object. Stores product info.
    '''

    re_usd = re.compile("\$[0-9]+\.[0-9]+")
    re_desc = re.compile('<.*?>')
    re_mah = re.compile('(?<=\s)[0-9]+(?=mah\s)', re.IGNORECASE)
    re_cells = re.compile('(?<=\s)[0-9]+(?=s\s)', re.IGNORECASE)

    def __init__(self, **kwargs):
        self.URL = kwargs['url']
        self.LISTINGS = []
        self.PAGES = []

    def get_index(self):
        r = requests.get(self.URL)
        if r.status_code == 200:
            self.INDEX = BeautifulSoup(r.text)
        else:
            return None

    def get_pages(self):
        tags = self.INDEX.findAll('form', {'class': 'paging'})
        for tag in tags:
            lis = tag.findAll('li')
            for li in lis:
                links = li.findAll('a')
                for link in links:
                    self.PAGES.append((link.text, link['href']))

    def get_page(self, **kwargs):
        return requests.get(kwargs['url'])


    @classmethod
    def parse_listing(self, listing):

        LISTING = {
            'price': None,
            'cells': None,
            'capacity': None,
            'link': None,
        }

        # Description is in ANCHOR tag (has capacity, and cell count)
        descriptiontags = listing.find_all('a')
        for description in descriptiontags:
            text = description.renderContents().strip()
            if not self.re_desc.match(text):
                try:
                    LISTING['capacity'] = self.re_mah.findall(text)[0]
                    LISTING['cells'] = self.re_cells.findall(text)[0]
                    LISTING['link'] = 'http://www.hobbyking.com/hobbyking/store/' + description['href']
                except IndexError:
                    return None

        # Price is currently in FONT tag
        fonttags = listing.findAll('font')
        for fonttag in fonttags:
            text = fonttag.renderContents()
            if self.re_usd.match(text):
                LISTING['price'] = self.re_usd.findall(text)[0]

        return LISTING


    def get_listings(self, **kwargs):

        self.LISTINGS.append(self.parse_listing(self.INDEX))

        for page in self.PAGES:

            listings = page[2].findAll('tr', {'class': 'zeroLineHeight'})

            for listing in listings:
                if listing:
                    self.LISTINGS.append(self.parse_listing(listing))


if __name__ == '__main__':
    import settings
    import json

    crawler = Crawler(url=settings.URL)
    crawler.get_index()

    # For "production"
    crawler.get_pages()
    for i, page in enumerate(crawler.PAGES):
        crawler.PAGES[i] = (page[0], page[1], BeautifulSoup(crawler.get_page(url='http://www.hobbyking.com/hobbyking/store/'+page[1]).text))

    # For testing
    #crawler.PAGES.append((1, settings.URL, crawler.INDEX))

    crawler.get_listings()

    print json.dumps(crawler.LISTINGS)

