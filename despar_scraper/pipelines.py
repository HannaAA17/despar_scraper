# %%writefile /content/despar_scraper/despar_scraper/pipelines.py

# useful for handling different item types with a single interface
from scrapy.spiders import Spider
from itemadapter import ItemAdapter


from .items import DesparStoreItem, DesparCategoryItem, DesparProductItem, DesparPromoItem, DesparProductDetailsItem


def __process_store_item(item_data: dict) -> dict:
    item = DesparStoreItem(**item_data)
    return item

def __process_category_item(item_data: dict) -> dict:
    item = DesparCategoryItem(**item_data)
    return item

def __process_product_item(item_data: dict) -> dict:
    item = DesparProductItem(**item_data)
    return item

def __process_promo_item(item_data: dict) -> dict:
    item = DesparPromoItem(**item_data)
    return item

def __process_product_detail_item(item_data: dict) -> dict:
    item = DesparProductDetailsItem(**item_data)
    return item

ITEM_MAP = {
    'store': __process_store_item,
    'category': __process_category_item,
    'product': __process_product_item,
    'promo': __process_promo_item,
    'product_details': __process_product_detail_item,
}

class DesparScraperPipeline:
    def process_item(self, item: dict, spider: Spider):
        
        if spider.name == '1_stores':
            item_type = item.pop('item_type')
            return ITEM_MAP[item_type](item)

        if spider.name == '2_product_list':
            item_type = item.pop('item_type')
            return ITEM_MAP[item_type](item)
        
        if spider.name == '3_product_details':
            item_type = item.pop('item_type')
            return ITEM_MAP[item_type](item)
        
        return item
