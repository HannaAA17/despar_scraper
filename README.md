```bash
scrapy crawl 1_stores -a store="https://shop.despar.com"
```

``` bash
scrapy crawl 2_product_list -a dev=True
```

```bash
scrapy crawl 3_product_details -a dev=True
```

---


https://{ domain }/spesa-consegna-domicilio/{ zip_code }
https://{ domain }/spesa-ritiro-negozio/{ store_slug }

{ store_url }/{ category_slug }
{ store_url }/prodotto/{ product_id }
{ store_url }/ajax/productsPagination?{ category_id, page_num }

