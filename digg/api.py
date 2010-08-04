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
            return self.__class__(endpoint=self.endpoint, methodname='.'.join((self.methodname, k)).lstrip('.'), user_agent=self.user_agent, oauth_consumer=self.oauth_consumer, cache=self.cache)

    def _extend_params(self, params):
        params['method'] = self.methodname
        params['type'] = 'json'
        return params

    def _build_request_url(self, params, kwargs, post=False):
        """
        Build URL to send API query to.
        
        - params: dictionary of parameters
        - kwargs: urlencoded contents of params
        - post:   boolean
        """
        if post:
            return '%s?method=%s&type=%s' % (self.endpoint, self.methodname, params.get('type', 'json'))
        else:
            return '%s?%s' % (self.endpoint, kwargs)

    def __call__(self, **params):
        params = self._extend_params(params)
        kwargs = dict(params)
        kwargs = urlencode(kwargs)
        if self.methodname in POST_ACTIONS:
            # HTTP POST
            request_url = self._build_request_url(params, kwargs, post=True)
            client = oauth.SimpleClient(self.oauth_consumer, token=params.get('oauth_token', None))
            if 'oauth_token' in params:
                del params['oauth_token']
            req = client.request(self.endpoint, 'POST', params)
            handle = urllib2.urlopen(req)

            # POST responses aren't cached or  deserialized,
            # as OAuth methods return non-json bodies
            return handle.read()
        else:
            if self.cache != None:
                value = self.cache.get('diggapi-' + kwargs)
                if value:
                    return json.loads(value)

            # HTTP GET
            req = urllib2.Request(self._build_request_url(params, kwargs))
            cache_response = True

        if self.user_agent:
            req.add_header('User-Agent', self.user_agent)
        
        try:
            handle = urllib2.urlopen(req)
            response = handle.read()
            if cache_response and self.cache != None:
                self.cache.set('diggapi-' + kwargs, response, time=int(time() + 60))
            response = json.loads(response)
            return response
        except urllib2.HTTPError, e:
            raise DiggError('Digg sent status %i for method: %s\ndetails: %s' % (e.code, self.methodname, e.fp.read()))

class Digg(DiggCall):
    def __init__(self, endpoint='http://services.digg.com/1.0/endpoint', methodname='', user_agent='python-digg/1.2', oauth_consumer=None, cache=None):
        DiggCall.__init__(self, endpoint, methodname=methodname, user_agent=user_agent, oauth_consumer=oauth_consumer, cache=cache)

class Digg2(DiggCall):
    "Client for V2 of Digg API."
    def __init__(self, endpoint='http://services.new.digg.com/2.0/', methodname='', user_agent='python-digg/1.2', oauth_consumer=None, cache=None):
        DiggCall.__init__(self, endpoint=endpoint, methodname=methodname, user_agent=user_agent, oauth_consumer=oauth_consumer, cache=cache)

    def _extend_params(self, params):
        params['type'] = 'json'
        return params

    def _build_request_url(self, params, kwargs, post=False):
        """
        Build URL to send API query to.
        
        - params: dictionary of parameters
        - kwargs: urlencoded contents of params
        - post:   boolean
        """
        if post:
            return '%s.%s?type=%s' % (self.endpoint, self.methodname, params.get('type', 'json'))
        else:
            return '%s%s?%s' % (self.endpoint, self.methodname, kwargs)

__all__ = ['Digg', 'Digg2']
