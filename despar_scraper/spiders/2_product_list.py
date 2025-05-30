# %%writefile /content/despar_scraper/despar_scraper/spiders/2_product_list.py

import json
import scrapy
from scrapy.http import HtmlResponse


class ProductListSpider(scrapy.Spider):
    name = '2_product_list'
    allowed_domains = ['shop.desparsicilia.it', 'shop.despar.com']

    # FEEDS
    custom_settings = {
        'LOG_FILE': 'data/log/product_list.log',
        
        'FEEDS': {
            'data/json/categories.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparCategoryItem'],   
            },
            'data/json/product_list.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparProductItem'],
            },
            'data/json/promos.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparPromoItem'],
            },
        }
    }

    def __init__(self, store_list_file='data/json/stores.json', store_limit='0', category_limit='0', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_list_file = store_list_file
        self.category_limit = int(category_limit)
        self.store_limit = int(store_limit)

    async def start(self):
        # open json file in async function
        with open(self.store_list_file, 'r') as f:
            store_list = json.load(f) if not self.store_limit else json.load(f)[:self.store_limit]
        
        for store in store_list:
            yield scrapy.Request(
                url=store['url'],
                callback=self.parse__get_categories,
                meta={'store': store}
            )

    def parse__get_categories(self, response: HtmlResponse):
        store = response.meta['store']
        cat_count = 0
        # Extract categories
        for main_tag in response.css('div.main-navigation__item--container'):
            main_category = main_tag.css('div.main-navigation__item--title > span::text').get(default='').strip()

            for sub_tag in main_tag.css('div.main-navigation__item--side-content > div.grid > div.columns__item'):
                sub_tag_tag = sub_tag.css('div.columns__item--mobile > a')
                sub_category = sub_tag_tag.css('h4::text').get(default='').strip()
                sub_category_href = sub_tag_tag.attrib.get('href', '')
                sub_category_slug = sub_category_href.split('/')[-1]
                sub_category_id = sub_category_slug.split('_')[-1] if '_' in sub_category_slug else ''
                
                for tag in sub_tag.css('div.columns__item--sub > div > a'):
                    category = tag.css('::text').get(default='').strip()
                    category_href = tag.attrib.get('href', '')
                    category_slug = category_href.split('/')[-1]
                    category_id = category_slug.split('_')[-1] if '_' in category_slug else ''
                    
                    category_data = {
                        'item_type': 'category',
                        'main_category': main_category,
                        'sub_category': sub_category,
                        'sub_category_slug': sub_category_slug,
                        'sub_category_id': sub_category_id,
                        'category': category,
                        'category_slug': category_slug,
                        'category_id': category_id,
                        'category_hierarchy': ' > '.join([main_category, sub_category, category]), 
                        'store_pk': store['pk'],
                    }
                    
                    yield category_data

                    yield scrapy.FormRequest(
                        url=store['url']+'/ajax/productsPagination',
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
                        meta={
                            'store': store,
                            'category': category_data, 
                            'page': 1, 'attempt': 1
                        },
                    )

                    cat_count += 1
                    if self.category_limit:
                        if cat_count >= self.category_limit:
                            return None


    def parse__get_products_list(self, response: HtmlResponse):
        store = response.meta['store']
        category = response.meta['category']
        page = response.meta['page']
        attempt = response.meta['attempt']

        # Handle site errors/blocks
        try:
            # Try to parse JSON and extract HTML
            json_response = response.json()
            html = json_response.get('html', '')

            if not html:
                raise ValueError('Empty HTML in response')

        except ValueError as e:
            # Specific handling for JSON decode errors
            error_msg = 'Invalid JSON response for category {} page {}'.format(category['category_hierarchy'], page)
            yield self._handle_parse_error(response, e, error_msg, attempt)
            return None

        except Exception as e:
            # General exception handling
            error_msg = 'Unexpected error processing category {} page {}'.format(category['category_hierarchy'], page)
            yield self._handle_parse_error(response, e, error_msg, attempt)
            return None

        # Parse the HTML
        response_ = scrapy.Selector(text=html)

        # Select the products
        products = response_.css('section.product > div[data-id]')

        # Parse Products
        if not products:
            self.logger.warning('No products found for category {} page {}'.format(category['category_hierarchy'], page))
            return None

        for prod in products:
            product_data = {
                'item_type': 'product',
                'id_': prod.attrib.get('data-id'),
                'name': prod.attrib.get('data-name'),
                'brand': prod.attrib.get('data-brand'),
                'price': prod.attrib.get('data-price'),
                'old_price': prod.attrib.get('data-old-price'),
                'meta': prod.attrib.get('data-meta'),
                'icons': prod.css('div.special-icon  > span.icon[data-tooltip]::attr(data-tooltip)').getall(),
                'img': prod.attrib.get('data-img-src'),
                'category_id': category['category_id'], #
                'category_hierarchy': category['category_hierarchy'], #
                'store_pk': store['pk'], #
                'url': store['url']+'/prodotto/'+prod.attrib.get('data-id'),
            }
            yield product_data
            
            # get promo
            promo_tag = prod.css('div.product-badge')
            if promo_tag:
                promo_value_tag = promo_tag.css('div.promo-container > span')
                promo_data = {
                    'item_type': 'promo',
                    'product_id': product_data['id_'],
                    'type_': promo_value_tag.attrib['class'],
                    'value': promo_value_tag.css('::text').get(None),
                    'end_date': promo_tag.css('span.text::text').get(None),
                    'store_pk': store['pk'], #
                }
                yield promo_data

        # Check for next page
        if len(products) == 40:
            yield scrapy.FormRequest(
                url=response.url,
                formdata={
                    'page_num': str(page + 1),
                    'category_id': category['category_id'],
                    'page_container': '1',
                    'featured_category_id': '0',
                    'productsPerPage': '40',
                    'params': '?sort=asc',
                    'special_id': '',
                },
                callback=self.parse__get_products_list,
                meta={
                    'store': store, 
                    'category': category, 
                    'page': page + 1, 'attempt': 1
                },
            )


    def _handle_parse_error(self, response: HtmlResponse, error, error_msg, attempt):
        max_attempts = 6

        if attempt < max_attempts:
            self.logger.warning(
                f'[Retry {attempt}/{max_attempts}] {error_msg}. Error: {str(error)}'
            )
            # Clone request with incremented attempt counter
            yield response.request.replace(
                meta={**response.meta, 'attempt': attempt + 1},
                dont_filter=True  # Ensure the retry isn't blocked by dupefilter
            )
        else:
            self.logger.error(
                f'Max retries ({max_attempts}) exceeded for {error_msg}. Error: {str(error)}'
            )