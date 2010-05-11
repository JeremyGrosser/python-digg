'''
Loosely based on Mike Verdone's excellent twitter library:
http://github.com/sixohsix/twitter/
'''

from exceptions import Exception
from urllib import urlencode
import httplib2

try:
    import json
except ImportError:
    import simplejson as json

from digg_globals import POST_ACTIONS

class MemoryCache(object):
    def __init__(self):
        self.data = {}

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            return None

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

class DiggError(Exception):
    """
    Exception thrown by the Digg object when there is an
    error interacting with digg.com.
    """
    pass

class DiggCall(object):
    def __init__(self, endpoint, methodname='', user_agent=None):
        self.endpoint = endpoint
        self.methodname = methodname
        self.user_agent = user_agent

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            return DiggCall(self.endpoint, '.'.join((self.methodname, k)).lstrip('.'))

    def __call__(self, **kwargs):
        kwargs['method'] = self.methodname
        kwargs['type'] = 'json'
        kwargs = urlencode(kwargs)
        headers = []


        if self.user_agent:
            headers.append(('User-Agent', self.user_agent))

        if self.methodname in POST_ACTIONS:
            raise NotImplementedError("This method requires OAuth, which hasn't been implemented yet")
            #response, content = httplib2.request('%s?method=%s' % (self.endpoint, self.methodname), method='POST', body=kwargs)
        
        http = httplib2.Http(cache=MemoryCache())
        response, content = http.request('%s?%s' % (self.endpoint, kwargs))
        if response.status == 200:
            return json.loads(content)
        else:
            raise DiggError('Digg sent status %i for method: %s\ndetails: %s' % (response.status, self.methodname, content))

class Digg(DiggCall):
    def __init__(self, endpoint='http://services.digg.com/1.0/endpoint', user_agent='python-digg/0.1'):
        DiggCall.__init__(self, endpoint=endpoint, user_agent=user_agent)

__all__ = ['Digg']
