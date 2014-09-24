from bs4 import BeautifulSoup

import requests

# We can speed up get_listings by running all of our requests in parallel
try:
    import grequests
except ImportError:
    pass

import re


class Crawler(object):
    """
    A basic crawler class. Intended to collect, store and process product info.
    """

    def __init__(self, **kwargs):
        self.base_url = kwargs['url']
        self.listings = []
        self.pages = []
        self.index = None

    def get_index(self):
        """
        Get the root index page
        """

        req = requests.get(self.base_url)
        if req.status_code == 200:
            self.index = BeautifulSoup(req.text)
        else:
            return None

    @staticmethod
    def get_page(url):
        """
        Get a page.
        ulr: The url to a page
        """

        return requests.get(url)

    @staticmethod
    def get_pages_concurrent(urls):
        """
        Get a bunch of pages in parallel
        ulr: The url to a page
        """

        responses = [grequests.get(u) for u in urls]
        responses = grequests.map(responses, size=10)
        return responses


class HKCrawler(Crawler):
    """
    A class that extends the base crawler class with some site-specific functions
    and helpful constants
    """

    re_usd = re.compile(r'\$[0-9]+\.[0-9]+')
    re_desc = re.compile(r'<.*?>')
    re_mah = re.compile(r'(?<=\s)[0-9]+(?=mah\s)', re.IGNORECASE)
    re_cells = re.compile(r'(?<=\s)[0-9]+(?=s\s)', re.IGNORECASE)

    def get_pages(self):
        """
        Compile a list of pages
        """

        tags = self.index.findAll('form', {'class': 'paging'})
        for tag in tags:
            lis = tag.findAll('li')
            for li in lis:
                links = li.findAll('a')
                for link in links:
                    self.pages.append((link.text, link['href']))

    def parse_listing(self, listing_text):
        """
        Tear apart and store a listing

        :param listing_text: The textual contents of a listing
        """

        listing = {
            'price': None,
            'cells': None,
            'capacity': None,
            'link': None,
        }

        # Description is in ANCHOR tag (has capacity, and cell count)
        description_tags = listing_text.find_all('a')
        for description in description_tags:
            text = description.renderContents().strip()
            if not self.re_desc.match(text):
                try:
                    listing['capacity'] = self.re_mah.findall(text)[0]
                    listing['cells'] = self.re_cells.findall(text)[0]
                    listing['link'] = (
                        'http://www.hobbyking.com'
                        '/hobbyking/store/'
                    )
                    listing['link'] += description['href']

                except IndexError:
                    return None

        # Price is currently in FONT tag
        font_tags = listing_text.findAll('font')
        for font_tag in font_tags:
            text = font_tag.renderContents()
            if self.re_usd.match(text):
                listing['price'] = self.re_usd.findall(text)[0]

        return listing

    def get_listings(self):
        """
        Fetch all listings
        """

        all_pages = []
        bodies = []
        urls = []

        try:

            # Get a list of links to follow
            for page in self.pages:
                urls.append('http://www.hobbyking.com/hobbyking/store/'+page[1])

            # Here is where this *try* block might fail (grequests not loadable)
            # loads all the pages in parallel
            all_pages = self.get_pages_concurrent(urls)

            # Populate the class's *pages* variable with existing contents,
            # extended with a BeautifulSoup object at the end of each tuple
            for i, page in enumerate(self.pages):
                self.pages[i] = (
                    page[0],
                    page[1],
                    BeautifulSoup(all_pages[i].text)
                )

        except NameError:

            # Getting all of the pages at once failed, so do them one by one,
            # yielding the same result as before
            for i, page in enumerate(self.pages):
                self.pages[i] = (
                    page[0],
                    page[1],
                    BeautifulSoup(self.get_page(
                        url='http://www.hobbyking.com/hobbyking/store/'+page[1]
                    ).text
                    )
                )

    def parse_listings(self):
        """
        Compile all listings
        """

        self.listings.append(self.parse_listing(self.index))

        for _page in self.pages:

            listings = _page[2].findAll('tr', {'class': 'zeroLineHeight'})

            for listing in listings:
                if listing:
                    self.listings.append(self.parse_listing(listing))

    @classmethod
    def crawl(cls, url):
        """
        :return: An instance of the crawler that has crawled and parsed listings
        """

        crawler = cls(url=url)
        crawler.get_index()
        crawler.get_pages()
        crawler.get_listings()
        crawler.parse_listings()

        return crawler


if __name__ == '__main__':
    import settings
    import json

    CRAWLER = HKCrawler.crawl(url=settings.URL)

    print json.dumps(CRAWLER.listings)
