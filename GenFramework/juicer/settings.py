import os

PROJECT_DIR = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

BOT_NAME = 'juicer'#already discussed
BOT_VERSION = '1.0' #already discusses

SPIDER_MODULES = ['juicer.spiders'] #done 
NEWSPIDER_MODULE = 'juicer.spiders'
DEFAULT_ITEM_CLASS = 'juicer.items.JuicerItem'

USER_AGENT = "Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0" 

ITEM_PIPELINES = {
    'juicer.validations_pipeline.ValidateRecordPipeline': 300,
    'juicer.pipelines.JuicerPipeline': 400,
}

#HTTPCACHE_ENABLED = True               #-> t.irue is we are enabling, false means cache is diabled#                     # Note: Disable Cache Option in Prod setup.
#HTTPCACHE_DIR = '%s/cache/' % PROJECT_DIR #-> path where cache should be saved 
#HTTPCACHE_EXPIRATION_SECS = 0 #cache expiration-> if we mention 10 here-> within 10 sec , the cache data willbe removed 
#HTTPCACHE_STORAGE = 'juicer.cache.LevelDBCacheStorage'

ROBOTSTXT_OBEY = 1 #-> robots.txt -> 1 means we are obeying robots
DOWNLOAD_DELAY = 0.25 #- > time betwwn the request and response
DOWNLOAD_TIMEOUT = 360 #-> if we dont get response from site with in 360 secs, the rquest will get timedout
RANDOMIZE_DOWNLOAD_DELAY = True

LOG_FILE = None #-> for every run, a log willl be saved as of a phone logs
LOG_LEVEL = 'INFO' #'DEBUG'
#LOG_LEVEL = 'DEBUG'


#DOWNLOADER_CLIENTCONTEXTFACTORY = 'juicer.contextfactory.MyClientContextFactory'
#DOWNLOADER_CLIENTCONTEXTFACTORY = 'juicer.contextfactory.MyClientContextFactory'
DOWNLOAD_HANDLERS_BASE = {
        'file': 'scrapy.core.downloader.handlers.file.FileDownloadHandler',
        'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
        'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
        's3': 'scrapy.core.downloader.handlers.s3.S3DownloadHandler',
        'ftp': 'scrapy.core.downloader.handlers.ftp.FTPDownloadHandler',
}


DB_HOST = 'localhost' 
DB_USERNAME = 'root'
DB_PASSWORD = 'e3e2b51caee03ee85232537ccaff059d167518e2'
URLQ_DATABASE_NAME = 'JWURLQUEUE'                         # Fill with actual DATABASE NAME.
#URLQ_DATABASE_NAME = 'JUSTWATCHRAWDB'

SCRIPT_LOG_FILE = 'juicer.log'
LOGS_DIR = '%s/logs/' % PROJECT_DIR

TELNETCONSOLE_ENABLED = False
WEBSERVICE_ENABLED = False

NUM_ITEMS_TO_CONSUME = 10000

CONCURRENT_SPIDERS = 16

SPIDER_MIDDLEWARES = {
    'juicer.utils.SpiderMiddleware': 10000,
}

'''
DOWNLOADER_MIDDLEWARES = {
    'juicer.utils.RandomUserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'juicer.middlewares.InterfaceRoundRobinMiddleware' : 1
}
'''
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

#DOWNLOADER_MIDDLEWARES = {
    #'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    #'scrapy_proxies.RandomProxy': 100,
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#}


'''DOWNLOADER_MIDDLEWARES = {
        'juicer.utils.RandomUserAgentMiddleware': 400,
        'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
        'juicer.middlewares.InterfaceRoundRobinMiddleware' : 1
}'''

DEFAULT_REQUEST_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
                'Accept-Encoding': '*'
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

USER_AGENT_LIST = ["Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0"]


PROXY_LIST = '/home/interns/Sneha/juicer/proxy.list'
