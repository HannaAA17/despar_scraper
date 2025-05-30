
import scrapy
from scrapy.http import HtmlResponse

from urllib.parse import urlparse

class ProductListSpider(scrapy.Spider):
    name = 'product_list'
    allowed_domains = ['shop.desparsicilia.it', 'shop.despar.com']


    def __init__(self, store, dev=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(store))
        self.dev = dev
        
        
    async def start(self):
        yield scrapy.Request(
            url=self.store,
            callback=self.parse__get_categories,
        )


    def parse__get_categories(self, response: HtmlResponse):
        for main_tag in response.css('div.main-navigation__item--container'):
            main_category = main_tag.css('div.main-navigation__item--title > span::text').get(default='').strip()

            for sub_tag in main_tag.css('div.main-navigation__item--side-content > div.grid > div.columns__item'):
                sub_tag_tag = sub_tag.css('div.columns__item--mobile > a')
                sub_category = sub_tag_tag.css('h4::text').get(default='').strip()
                sub_category_href = sub_tag_tag.attrib.get('href', '')
                sub_category_id = sub_category_href.split('_')[-1] if '_' in sub_category_href else ''

                for tag in sub_tag.css('div.columns__item--sub > div > a'):
                    category = tag.css('::text').get(default='').strip()
                    category_href = tag.attrib.get('href', '')
                    category_id = category_href.split('_')[-1] if '_' in category_href else ''

                    yield {
                        'item_type': 'category',
                        'main_category': main_category,
                        'sub_category': sub_category,
                        'sub_category_href': self.domain + sub_category_href,
                        'sub_category_id': sub_category_id,
                        'category': category,
                        'category_href': self.domain + category_href,
                        'category_id': category_id,
                    }

                    yield scrapy.FormRequest(
                        url=self.store+'/ajax/productsPagination',
                        formdata={
                            'page_num': '1',
                            'category_id': category_id,
                            'page_container': '1',
                            'featured_category_id': '0',
                            'productsPerPage': '40',
                            'params': '?sort=asc',
                            'special_id': '',
                        },
                        callback=self.parse__get_products_list,
                        meta={'category_id': category_id, 'page': 1, 'attempt': 1},
                    )
                
                    if self.dev:
                        return None


    def parse__get_products_list(self, response: HtmlResponse):
        category_id = response.meta['category_id']
        page = response.meta['page']
        attempt = response.meta.get('attempt', 1)

        # Handle site errors/blocks
        try:
            # Try to parse JSON and extract HTML
            json_response = response.json()
            html = json_response.get('html', '')

            if not html:
                raise ValueError("Empty HTML in response")

        except ValueError as e:
            # Specific handling for JSON decode errors
            error_msg = f"Invalid JSON response for category {category_id} page {page}"
            yield self._handle_parse_error(response, e, error_msg, attempt)
            return None

        except Exception as e:
            # General exception handling
            error_msg = f"Unexpected error processing category {category_id} page {page}"
            yield self._handle_parse_error(response, e, error_msg, attempt)
            return None

        # Parse the HTML
        response_ = scrapy.Selector(text=html)

        # Select the products
        products = response_.css('section.product > div[data-id]')

        # Parse Products
        if not products:
            self.logger.warning(f"No products found for category {category_id} page {page}")
            return None

        for prod in products:
            product_data = {
                'item_type': 'product',
                'id_': prod.attrib.get('data-id'),
                'name': prod.attrib.get('data-name'),
                'brand': prod.attrib.get('data-brand'),
                'price': prod.attrib.get('data-price'),
                'old_price': prod.attrib.get('data-old-price'),
                'category_id': category_id,
                'meta': prod.attrib.get('data-meta'),
                'img': prod.attrib.get('data-img-src'),
            }
            yield product_data
            
            # get promo
            promo_tag = prod.css('div.product-badge')
            if promo_tag:
                promo_value_tag = promo_tag.css('div.promo-container > span')
                promo_data = {
                    'item_type': 'promo',
                    'product_id': product_data['id_'],
                    'type': promo_value_tag.attrib['class'],
                    'value': promo_value_tag.css('::text').get(None),
                    'end_date': promo_tag.css('span.text::text').get(None),
                }
                yield promo_data

        # Check for next page
        if len(products) == 40:
            yield scrapy.FormRequest(
                url=response.url,
                formdata={
                    'page_num': str(page + 1),
                    'category_id': category_id,
                    'page_container': '1',
                    'featured_category_id': '0',
                    'productsPerPage': '40',
                    'params': '?sort=asc',
                    'special_id': '',
                },
                callback=self.parse__get_products_list,
                meta={'category_id': category_id, 'page': page + 1},
            )


    def _handle_parse_error(self, response: HtmlResponse, error, error_msg, attempt):
        max_attempts = 6

        if attempt < max_attempts:
            self.logger.warning(
                f"[Retry {attempt}/{max_attempts}] {error_msg}. Error: {str(error)}"
            )
            # Clone request with incremented attempt counter
            yield response.request.replace(
                meta={**response.meta, 'attempt': attempt + 1},
                dont_filter=True  # Ensure the retry isn't blocked by dupefilter
            )
        else:
            self.logger.error(
                f"Max retries ({max_attempts}) exceeded for {error_msg}. Error: {str(error)}"
            )
