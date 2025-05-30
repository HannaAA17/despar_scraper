## How to run
1) **Stores Spyder** scrapes stores info in the domain [[shop.despar.com](https://shop.despar.com), [shop.desparsicilia.it](https://shop.desparsicilia.it)]

    ```bash
    scrapy crawl 1_stores -a store="https://shop.despar.com"
    ```

2) **Product List Spyder** scrapes the categories, products-list on each category and the promos in this store

    ``` bash
    scrapy crawl 2_product_list -a store_limit=1 -a category_limit=3 
    ```

3) **Product Details Spyder** scrapes the product descriptions and images links 
    ```bash
    scrapy crawl 3_product_details -a product_limit=3
    ```

---

## Endpoints

```https://{domain}/spesa-consegna-domicilio/{zip_code}```

```https://{domain}/spesa-ritiro-negozio/{store_slug}```

```{store_url}/{category_slug}```

```{store_url}/prodotto/{product_id}```

```{store_url}/ajax/productsPagination?{category_id,page_num}```

