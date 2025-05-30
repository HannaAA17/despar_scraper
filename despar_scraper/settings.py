
BOT_NAME = "despar_scraper"

SPIDER_MODULES = ["despar_scraper.spiders"]
NEWSPIDER_MODULE = "despar_scraper.spiders"

ITEM_PIPELINES  = {
    'despar_scraper.pipelines.DesparScraperPipeline': 300
}

ADDONS = {}

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1

RETRY_ENABLED = True
RETRY_HTTP_CODES = [403, 500, 502, 503, 504, 522, 524, 408]
RETRY_TIMES = 5  # Number of times to retry

DEFAULT_REQUEST_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'dnt': '1',
    'priority': 'u=0, i',
    'referer': 'https://shop.desparsicilia.it/',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
}

# feed to output/file.json
FEEDS = {
    'data/categories.json': {
        'format': 'json',
        'overwrite': True,
        'encoding': 'utf-8',
        'item_classes': ['despar_scraper.items.DesparCategoryItem'],   
    },
    'data/products.json': {
        'format': 'json',
        'overwrite': True,
        'encoding': 'utf-8',
        'item_classes': ['despar_scraper.items.DesparProductItem'],
    },
    'data/promos.json': {
        'format': 'json',
        'overwrite': True,
        'encoding': 'utf-8',
        'item_classes': ['despar_scraper.items.DesparPromoItem'],
    },
    'data/all.json': {
        'format': 'json',
        'overwrite': True,
        'encoding': 'utf-8',
    }
}


LOG_ENABLED = True  
LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL in console
LOG_FILE = 'data/debug.log'  
LOG_FILE_APPEND = False 
