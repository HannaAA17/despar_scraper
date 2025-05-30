
# useful for handling different item types with a single interface
from scrapy.spiders import Spider
from itemadapter import ItemAdapter


from .items import DesparCategoryItem, DesparProductItem, DesparPromoItem


def __process_category_item(item_data: dict) -> dict:
    item = DesparCategoryItem(**item_data)
    return item

def __process_product_item(item_data: dict) -> dict:
    item = DesparProductItem(**item_data)
    return item

def __process_promo_item(item_data: dict) -> dict:
    item = DesparPromoItem(**item_data)
    return item

ITEM_MAP = {
    'category': __process_category_item,
    'product': __process_product_item,
    'promo': __process_promo_item
}

class DesparScraperPipeline:
    def process_item(self, item: dict, spider: Spider):
        if spider.name == 'product_list':
            item_type = item.pop('item_type')
            return ITEM_MAP[item_type](item)
        return item
