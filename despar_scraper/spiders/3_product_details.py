# %%writefile /content/despar_scraper/despar_scraper/spiders/product_details.py

import json
import scrapy
from scrapy.http import HtmlResponse

class ProductDetailsSpider(scrapy.Spider):
    name = '3_product_details'
    allowed_domains = ['shop.desparsicilia.it', 'shop.despar.com']

    # feed
    custom_settings = {
        'LOG_FILE': 'data/log/product_details.log',
        'FEEDS': {
            'data/json/product_details.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparProductDetailsItem'],   
            },
        }
    }
    
    def __init__(self, product_list_file='data/json/product_list.json', dev=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_list_file = product_list_file
        self.dev = dev
        
    async def start(self):
        # open json file in async function
        with open(self.product_list_file, 'r') as f:
            product_list = json.load(f) if not self.dev else json.load(f)[:10]
        
        for prod in product_list:
            yield scrapy.Request(
                url=prod['url'],
                callback=self.parse__get_product_details,
                meta={'product_id': prod['id_']}
            )

    def parse__get_product_details(self, response: HtmlResponse):
        
        images = ( 
            response.css('div#ulImage img[data-zoom]::attr(data-zoom)') 
            or response.css('div.main-pic img[data-zoom]::attr(data-zoom)') 
        ).getall()

        description = {}
        for des_tag in response.css('ul.accordion > li'):
            tab_name = des_tag.css('h3::text').get('').replace('\xa0', '')
            tab_content = des_tag.css('div.acc-content').extract_first()
            description[tab_name] = tab_content
        
        yield {
            'item_type': 'product_details',
            'product_id': response.meta['product_id'],
            'images': images,
            'description': description
        }
