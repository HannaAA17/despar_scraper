# %%writefile /content/despar_scraper/despar_scraper/spiders/1_stores.py

import scrapy, re, json
from scrapy.http import HtmlResponse
from urllib.parse import urlparse


class ProductListSpider(scrapy.Spider):
    name = '1_stores'
    allowed_domains = ['shop.desparsicilia.it', 'shop.despar.com']

    custom_settings = {
        'LOG_FILE': 'data/log/stores.log',
        'FEEDS': {
            'data/json/stores.json': {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparStoreItem'],   
            },
            'data/csv/stores.csv': {
                'format': 'csv',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_classes': ['despar_scraper.items.DesparStoreItem'],   
            },
        }
    }

    def __init__(self, store, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(store))
        self.atHome = {}
        self.atStore = {}
    
    async def start(self):
        yield scrapy.Request(
            url=self.store,
            callback=self.parse_store,
        )

    def parse_store(self, response: HtmlResponse):
        
        province = {}
        for option in response.css('select#delivery-province option[value]'):
            province[option.attrib.get('value')] = option.css('::text').get()

        atHomeCitiesJson = json.loads(re.search('jsonInfo.atHomeCitiesJson = ({.+});', response.text).group(1))
        atHomeZipCodeItems = json.loads(re.search('jsonInfo.atHomeZipCodeItems = ({.+});', response.text).group(1))
        atStoreCitiesJson = json.loads(re.search('jsonInfo.atStoreCitiesJson = ({.+});', response.text).group(1))
        storesJson = json.loads(re.search('jsonInfo.storesJson = ({.+});', response.text).group(1))
        stores4MapsJson = json.loads(re.search('jsonInfo.stores4MapsJson = (.+);', response.text).group(1))
        stores4MapsJson = {s['StoreId']: s for s in stores4MapsJson}

        atStore_df_list = []
        for province_id in atStoreCitiesJson:
            for at_store_city in atStoreCitiesJson[province_id]:
                for store in storesJson[str(at_store_city['Id'])]:
                    stores4MapsJson_item = stores4MapsJson.get(store['Id'], {})
                    store_data = {       
                        'item_type': 'store',
                        'domain': self.domain,
                        'type_': 'spesa-ritiro-negozio',
                        'slug': stores4MapsJson_item.get('Url', '').split('/')[-1],
                        'id_': str(store['Id']),
                        'name': store['Name'],
                        'address': stores4MapsJson_item.get('Address', ''),
                        'lat': stores4MapsJson_item.get('Lat', ''),
                        'long': stores4MapsJson_item.get('Long', ''),
                        'city_id': at_store_city['Id'],
                        'city_name': at_store_city['Name'],
                        'province_id': province_id,
                        'province_name': province.get(province_id, ''),
                    }
                    atStore_df_list.append({
                        'pk': ';'.join(store_data[k] for k in ['domain', 'type_', 'slug', 'id_']),
                        **store_data,
                        'url': '/'.join(store_data[k] for k in ['domain', 'type_', 'slug']),
                    })

        yield from atStore_df_list
        self.atStore.update({ x['id_']: x for x in atStore_df_list })

        atHome_df_list = []
        for province_id in atHomeCitiesJson:
            for at_home_city in atHomeCitiesJson.get(province_id, []):
                for zip_code in atHomeZipCodeItems[str(at_home_city['Id'])]:
                    atHome_df_list.append({
                        'province_id': province_id,
                        'province_name': province.get(province_id, ''),
                        'city_id': at_home_city['Id'],
                        'city_name': at_home_city['Name'],
                        'zip_code': zip_code['Id'],
                    })
        
        for atHome_store in atHome_df_list:
            yield scrapy.Request(
                url=self.store+'/spesa-consegna-domicilio/'+atHome_store['zip_code'],
                callback=self.parse_atHome_store,
                meta={'atHome_store': atHome_store},
            )
        
    def parse_atHome_store(self, response: HtmlResponse):
        store = response.meta['atHome_store']
        
        # get data using regular expression
        current_store_text = response.xpath('/html/body/script[contains(text(),"jsonInfo.currentStoreSlug")]/text()').get('')

        store['id'] = re.search('jsonInfo.currentStoreId = "(.+)";', current_store_text).group(1)
        atStore_item = self.atStore.get(store['id'], {})
        
        store_data = {
            'item_type': 'store',
            'domain': self.domain,
            'type_': 'spesa-consegna-domicilio',
            'slug': store['zip_code'],
            'id_': store['id'],
            'name': atStore_item.get('name', ''),
            'address': atStore_item.get('address', ''),
            'lat': atStore_item.get('lat', ''), 
            'long': atStore_item.get('long', ''), 
            'city_id': store['city_id'],
            'city_name': store['city_name'],
            'province_id': store['province_id'],
            'province_name': store['province_name'],
        }
        
        yield {
            'pk': ';'.join(store_data[k] for k in ['domain', 'type_', 'slug', 'id_']),
            **store_data,
            'url': '/'.join(store_data[k] for k in ['domain', 'type_', 'slug']),
        }