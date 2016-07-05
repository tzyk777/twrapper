import json
import tweepy
import logging
import sys
from tweepy.streaming import StreamListener, Stream
from .utils import _require_connection


class WrapperListener(StreamListener):
    def __init__(self, auth, callback, tracks, async, logger=None):
        self.auth = auth
        self.tracks = tuple(tracks)
        self.callback = callback
        self.async = async
        if not logger:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            self.logger = logging.getLogger()
        else:
            self.logger = logger
        self.connected = False

    def listen(self):
        self.stream = Stream(self.auth, self)
        self.stream.filter(track=self.tracks, async=self.async)
        self.connected = True
        self.logger.info('{} is listening.'.format(self))

    def disconnect(self):
        self.stream.disconnect()
        self.logger.info('{} is disconnected'.format(self))

    def on_data(self, raw_data):
        self.logger.info('New tweet received.')
        try:
            tweet = json.loads(raw_data)
            self.callback(tweet)
        except:
            pass

        return True

    def on_error(self, status_code):
        if status_code == 420:
            self.logger.warn('{} exceeded rate limit, take a 15 minutes nap'.format(self))
        return True

    def __str__(self):
        return 'Stream listener which interests in {}'.format(','.join(self.tracks))

    def __hash__(self):
        return hash(self.tracks)

    def __eq__(self, other):
        return self.tracks == other.tracks


class WrapperClient:
    def __init__(self, url, logger=None):
        self.url = url
        if not all(url):
            raise ValueError('Incomplete connection information.')
        self.consumer_key, self.consumer_secret, self.access_key, self.access_secret = self.url
        if not logger:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)
            self.logger = logging.getLogger()
        else:
            self.logger = logger
        self.connected = False

        self._subscriptions = {}

    def __str__(self):
        return 'WrapperClient'

    def connect(self):
        if self.connected:
            self.logger.warn('Client is already connected.')
            return
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.client = tweepy.API(self.auth)
        self.connected = True
        self.logger.info('WrapperClient is connected.')

    def disconnect(self):
        if not self.connected:
            self.logger.warn('WrapperClient Already disconnected.')
            return
        self.connected = False

    @property
    @_require_connection
    def me(self):
        return self.client.me()

    @_require_connection
    def subscribe(self, callback, tracks=None, async=False):
        if not callable(callback):
            raise ValueError('Must provide a callable function to WrapperListener class')
        listener = WrapperListener(self.auth, callback, tracks, async, self.logger)
        listener.listen()
        self._subscriptions[listener] = listener
        return listener

    def unsubscribe(self, listener):
        if listener in self._subscriptions:
            self._subscriptions[listener].disconnect()
            del self._subscriptions[listener]

    def unsubscribe_all(self):
        for listener in self._subscriptions:
            self._subscriptions[listener].disconnect()
        self._subscriptions = {}



