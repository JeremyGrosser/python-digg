'''
Loosely based on Mike Verdone's excellent twitter library:
http://github.com/sixohsix/twitter/
'''

from exceptions import Exception
from urllib import urlencode
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from time import time

from digg_globals import POST_ACTIONS
import oauth

class DiggError(Exception):
    """
    Exception thrown by the Digg object when there is an
    error interacting with digg.com.
    """
    pass

class DiggCall(object):
    def __init__(self, endpoint, methodname='', user_agent=None, oauth_consumer=None, cache=None):
        self.endpoint = endpoint
        self.methodname = methodname
        self.user_agent = user_agent
        self.oauth_consumer = oauth_consumer
        self.cache = cache

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            return DiggCall(self.endpoint, '.'.join((self.methodname, k)).lstrip('.'), user_agent=self.user_agent, oauth_consumer=self.oauth_consumer, cache=self.cache)

    def __call__(self, **params):
        params['method'] = self.methodname
        params['type'] = 'json'
        kwargs = dict(params)
        kwargs = urlencode(kwargs)

        if self.methodname in POST_ACTIONS:
            # HTTP POST
            request_url = '%s?method=%s&type=json' % (self.endpoint, self.methodname)
            client = oauth.SimpleClient(self.oauth_consumer, token=params.get('oauth_token', None))
            if 'oauth_token' in params:
                del params['oauth_token']
            req = client.request(self.endpoint, 'POST', params)
            handle = urllib2.urlopen(req)

            # POST responses aren't cached or  deserialized,
            # as OAuth methods return non-json bodies
            return handle.read()
        else:
            try:
                if self.cache:
                    value = self.cache.get('diggapi-' + kwargs)
                    if value:
                        return json.loads(value)
            except:
                pass

            # HTTP GET
            req = urllib2.Request('%s?%s' % (self.endpoint, kwargs))
            cache_response = True

        if self.user_agent:
            req.add_header('User-Agent', self.user_agent)
        
        try:
            handle = urllib2.urlopen(req)
            response = handle.read()
            if cache_response and self.cache != None:
                try:
                    self.cache.set('diggapi-' + kwargs, response, time=int(time() + 60))
                except:
                    pass
            response = json.loads(response)
            return response
        except urllib2.HTTPError, e:
            raise DiggError('Digg sent status %i for method: %s\ndetails: %s' % (e.code, self.methodname, e.fp.read()))

class Digg(DiggCall):
    def __init__(self, endpoint='http://services.digg.com/1.0/endpoint', user_agent='python-digg/0.1', oauth_consumer=None, cache=False):
        DiggCall.__init__(self, endpoint=endpoint, user_agent=user_agent, oauth_consumer=oauth_consumer, cache=cache)

__all__ = ['Digg']
