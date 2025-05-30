
import scrapy


class DesparCategoryItem(scrapy.Item):
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    sub_category_href = scrapy.Field()
    sub_category_id = scrapy.Field()
    category = scrapy.Field()
    category_href = scrapy.Field()
    category_id = scrapy.Field()

class DesparProductItem(scrapy.Item):
    id_ = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    category_id = scrapy.Field()
    meta = scrapy.Field()
    img = scrapy.Field()

class DesparPromoItem(scrapy.Item):
    product_id = scrapy.Field()
    type_ = scrapy.Field()
    value = scrapy.Field()
    end_date = scrapy.Field()

