# coding: utf-8
import urllib
import urllib2
import json

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 4300
DEFAULT_SCHEME = 'http'


class Client(object):
    PATH_START = '/start'
    PATH_STOP = '/stop'
    PATH_STATUS = '/status'

    def __init__(self, host=None, port=None, scheme=None):
        self.host = host or DEFAULT_HOST
        self.port = port or DEFAULT_PORT
        self.scheme = scheme or DEFAULT_SCHEME

    def __repr__(self):
        return '<%s: %s:%s>' % (self.__class__.__name__, self.host, self.port)

    def build_url(self, path):
        """URL構築
        """
        return '%s://%s:%s%s' % (self.scheme, self.host, self.port, path)

    def json_loads(self, data):
        return json.loads(data)

    def status(self):
        """ステータス情報
        """
        url = self.build_url(self.PATH_STATUS)
        result = self.http_get(url).read()
        return self.json_loads(result)

    def start(self, username, password, dispnum):
        """起動
        """
        url = self.build_url(self.PATH_START)
        result = self.http_post(url,
            username=username,
            password=password,
            dispnum=dispnum).read()
        return self.json_loads(result)

    def stop(self, pid):
        """停止
        """
        url = self.build_url(self.PATH_STOP)
        result = self.http_post(url,
            pid=pid).read()
        return self.json_loads(result)

    def urlopen(self, url, post_params=None):
        """urlopenのラッパー
        """
        return urllib2.urlopen(url, post_params)
        
    def urlencode(self, data):
        """urlencodeのラッパー
        """
        return urllib.urlencode(data)

    def http_get(self, url, **params):
        get_params = self.urlencode(params)
        if params:
            return self.urlopen('%s?%s' % (url, get_params))
        else:
            return self.urlopen(url)

    def http_post(self, url, **params):
        post_params = self.urlencode(params)
        return self.urlopen(url, post_params)
