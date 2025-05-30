# %%writefile /content/despar_scraper/despar_scraper/items.py

import scrapy

class DesparStoreItem(scrapy.Item):
    pk = scrapy.Field()
    domain = scrapy.Field()
    type_ = scrapy.Field()
    slug = scrapy.Field()
    id_ = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    lat = scrapy.Field()
    long = scrapy.Field()
    city_id = scrapy.Field()
    city_name = scrapy.Field()
    province_id = scrapy.Field()
    province_name = scrapy.Field()
    url = scrapy.Field()
    
class DesparCategoryItem(scrapy.Item):
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    sub_category_id = scrapy.Field()
    sub_category_slug = scrapy.Field()
    category = scrapy.Field()
    category_id = scrapy.Field()
    category_slug = scrapy.Field()
    category_hierarchy = scrapy.Field()
    store_pk = scrapy.Field()

class DesparProductItem(scrapy.Item):
    id_ = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    meta = scrapy.Field()
    icons = scrapy.Field()
    img = scrapy.Field()
    category_id = scrapy.Field()
    category_hierarchy = scrapy.Field()
    store_pk = scrapy.Field()
    url = scrapy.Field()

class DesparPromoItem(scrapy.Item):
    product_id = scrapy.Field()
    type_ = scrapy.Field()
    value = scrapy.Field()
    end_date = scrapy.Field()
    store_pk = scrapy.Field()

class DesparProductDetailsItem(scrapy.Item):
    product_id = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
