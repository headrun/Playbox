import os

PROJECT_DIR = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

BOT_NAME = 'juicer'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['juicer.spiders']
NEWSPIDER_MODULE = 'juicer.spiders'
DEFAULT_ITEM_CLASS = 'juicer.items.JuicerItem'

#USER_AGENT = "Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0"
USER_AGENT  = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785"

ITEM_PIPELINES = {
    'juicer.validations_pipeline.ValidateRecordPipeline': 300,
    'juicer.pipelines.JuicerPipeline': 400,
}

HTTPCACHE_ENABLED = False                                    # Note: Disable Cache Option in Prod setup.
HTTPCACHE_DIR = '%s/cache/' % PROJECT_DIR
HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_STORAGE = 'juicer.cache.LevelDBCacheStorage'

ROBOTSTXT_OBEY = 1
DOWNLOAD_DELAY = 1 
DOWNLOAD_TIMEOUT = 360
RANDOMIZE_DOWNLOAD_DELAY = True

LOG_FILE = None
#LOG_LEVEL = 'DEBUG' #'DEBUG'
LOG_LEVEL = 'INFO'
# DB Details
DB_HOST = 'localhost'
DB_USERNAME = 'root'
DB_PASSWORD = ''
URLQ_DATABASE_NAME = 'urlqueue_dev'                         # Fill with actual DATABASE NAME.

SCRIPT_LOG_FILE = 'juicer.log'
LOGS_DIR = '%s/logs/' % PROJECT_DIR

TELNETCONSOLE_ENABLED = False
WEBSERVICE_ENABLED = False

NUM_ITEMS_TO_CONSUME = 10000

CONCURRENT_SPIDERS = 16


SPIDER_MIDDLEWARES = {
    'juicer.utils.SpiderMiddleware': 10000,
}

DOWNLOADER_MIDDLEWARES = {
    'juicer.utils.RandomUserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
}

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'Accept-Encoding': '*'
}

RANDOM_SCHEDULING = True

DUMPSTORE_DIR = "%s/output_dir/" % PROJECT_DIR

DEFAULT_CRAWLER_PRIORITY = 5

MIN_URLS_TO_GET = 10

NO_ITEMS_TO_PROCESS = 100
NO_URLS_TO_PROCESS = 10000
NO_DUMPSTORE_ITEMS_TO_PROCESS = 10000

COUNTER_PREFIX  = "services.intervod.stats"

#USER_AGENT_LIST = ["Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0"]
USER_AGENT_LIST = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785"]
