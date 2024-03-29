from OpenSSL import SSL
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory

from twisted.internet.ssl import ClientContextFactory
from twisted.internet._sslverify import ClientTLSOptions
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory

class CustomClientContextFactory(ScrapyClientContextFactory):
    def getContext(self, hostname=None, port=None):
        ctx = ClientContextFactory.getContext(self)
        # Enable all workarounds to SSL bugs as documented by
        # http://www.openssl.org/docs/ssl/SSL_CTX_set_options.html
        ctx.set_options(SSL.OP_ALL)
        if hostname:
            ClientTLSOptions(hostname, ctx)
        return ctx

class MyClientContextFactory(ScrapyClientContextFactory):
    def __init__(self):
        self.method = SSL.SSLv23_METHOD
