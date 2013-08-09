from datetime import datetime
from itertools import cycle
from json import dumps
from random import shuffle
from socket import gethostname
from urlparse import urlparse

from circus import logger
from circus.stream import get_stream
from redis import StrictRedis
from redis.exceptions import ConnectionError
import traceback


# TODO
#
# Don't crash when redis is down
# Figure out if only full lines are sent (probably not)

class LogstashRedisLogger(object):

    def __init__(self, urls, service, redis_namespace, **kwargs):
        urls = urls.split(',')
        shuffle(urls)
        self._urls = cycle(urls)

        self._host = gethostname()
        self._redis_namespace = redis_namespace
        self._service = service
        self._substream = self.get_substream(**kwargs)
        self._fields = get_fields(**kwargs)

        self._redis = None
        self._pipeline = None

        self.connect()

    def __call__(self, data):
        self._substream(data)
        now = datetime.utcnow().isoformat() + 'Z'
        pid = data['pid']
        for line in data['data'].split('\n'):
            line = line.strip()
            if line:
                msg = self.format(now, line, data['name'], pid)
                self._pipeline.rpush(
                    self._redis_namespace,
                    msg,
                )

        try:
            self._pipeline.execute()
        except ConnectionError, e:
            traceback.print_exc()
            self.connect()

    def connect(self):
        if self._redis is not None:
            self._redis.connection_pool.disconnect()
            self._redis = None
        self._pipeline = None

        url = self._urls.next()
        logger.info('Will try to ship logs to {0}'.format(url))
        _url = urlparse(url, scheme='redis')
        _, _, _db = _url.path.rpartition('/')

        self._redis = StrictRedis(host=_url.hostname, port=_url.port, db=int(_db), socket_timeout=10)
        self._pipeline = self._redis.pipeline(transaction=False)


    def format(self, timestamp, line, channel, pid):
        return dumps({
            '@source': 'circus://{0}/{1}'.format(self._host, self._service),
            '@type': 'circus',
            '@tags': [self._service],
            '@fields': self._fields,
            '@timestamp': timestamp,
            '@source_host': self._host,
            '@source_path':  'circus:{0}:{1}:{2}'.format(self._service, pid, channel),
            '@message': line,
        })

    def get_substream(self, **kwargs):
        klass = kwargs.pop('subclass', None)
        if not klass:
            return null_stream

        new_args = {'class': klass}

        for key, value in kwargs.iteritems():
            if key.startswith('subclass'):
                new_args[key[9:]] = value
        return get_stream(new_args)['stream']


def get_fields(**kwargs):
    fields = {}
    for key, value in kwargs.iteritems():
        if key.startswith('field_'):
            fields[key[6:]] = value
    return fields


def null_stream(*args, **kwargs):
    pass
