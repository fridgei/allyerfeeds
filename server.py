import asyncmongo
import tornado.ioloop
from ConfigParser import ConfigParser
import feedparser
from functools import partial
from tornado import httpclient


class FeedHandler(tornado.ioloop.PeriodicCallback):
    def make_req(self, url):
        http_client = httpclient.AsyncHTTPClient()
        http_client.fetch(url, self.handle_req)

    def handle_req(self, response):
        if response.error:
            print "Error in response", response.error
        else:
            data = feedparser.parse(response.body)
            if 'feed' in data and 'ttl' in data['feed']:
                ttl = int(data['feed']['ttl'])
                self.set_callback_time(ttl)
            else:
                self.set_callback_time(60)
        #  WHAT DO???
        print data

    def __init__(self, callback_time, url, db):
        url = url
        self.callback_time = callback_time
        self.db = db
        super(tornado.ioloop.PeriodicCallback, self).__init__()
        self.io_loop = tornado.ioloop.IOLoop.instance()
        self.callback = partial(self.make_req, url=url)

    def set_callback_time(self, ttl):
        self.callback_time = ttl * 60000

def main():
    db = asyncmongo.Client(pool_id="test",
                           host="127.0.0.1",
                           port=27017,
                           mincached=10,
                           maxcached=20,
                           maxconnections=100,
                           dbname='test',
                           dbuser='testuser',
                           dbpass='testpass')
    y = FeedHandler(callback_time=6000,
            url='http://rss.cnn.com/rss/cnn_topstories.rss', db=db)
    y.start()
    y = FeedHandler(callback_time=6000,
            url='http://www.npr.org/rss/rss.php?id=1017', db=db)
    y.start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
