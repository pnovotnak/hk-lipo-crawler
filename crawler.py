from bs4 import BeautifulSoup

import requests

import re


class Crawler(object):
    """
    A crawler object. Stores product info.
    """

    re_usd = re.compile(r'\$[0-9]+\.[0-9]+')
    re_desc = re.compile(r'<.*?>')
    re_mah = re.compile(r'(?<=\s)[0-9]+(?=mah\s)', re.IGNORECASE)
    re_cells = re.compile(r'(?<=\s)[0-9]+(?=s\s)', re.IGNORECASE)

    def __init__(self, **kwargs):
        self.url = kwargs['url']
        self.listings = []
        self.pages = []
        self.index = None

    def get_index(self):
        """
        Get the root index page
        """
        req = requests.get(self.url)
        if req.status_code == 200:
            self.index = BeautifulSoup(req.text)
        else:
            return None

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

    @staticmethod
    def get_page(url):
        """
        Get a page.
        ulr: The url to a page
        """
        return requests.get(url)

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
        Compile all listings
        """

        self.listings.append(self.parse_listing(self.index))

        for _page in self.pages:

            listings = _page[2].findAll('tr', {'class': 'zeroLineHeight'})

            for listing in listings:
                if listing:
                    self.listings.append(self.parse_listing(listing))


if __name__ == '__main__':
    import settings
    import json

    CRAWLER = Crawler(url=settings.URL)
    CRAWLER.get_index()

    # For "production"
    CRAWLER.get_pages()
    for i, page in enumerate(CRAWLER.pages):
        CRAWLER.pages[i] = (
            page[0],
            page[1],
            BeautifulSoup(CRAWLER.get_page(
                url='http://www.hobbyking.com/hobbyking/store/'+page[1]
            ).text
            )
        )

    # For testing
    #CRAWLER.PAGES.append((1, settings.URL, CRAWLER.INDEX))

    CRAWLER.get_listings()

    print json.dumps(CRAWLER.listings)
