'''
Loosely based on Mike Verdone's excellent twitter library:
http://github.com/sixohsix/twitter/
'''

from exceptions import Exception
from urllib import urlencode
import urllib2
from rfc822 import parsedate
from time import time, mktime

try:
    import json
except ImportError:
    import simplejson as json

from digg_globals import POST_ACTIONS

class DiggError(Exception):
    """
    Exception thrown by the Digg object when there is an
    error interacting with digg.com.
    """
    pass

class DiggCall(object):
    def __init__(self, endpoint, methodname='', user_agent=None, cache=None):
        self.endpoint = endpoint
        self.methodname = methodname
        self.user_agent = user_agent
        self.cache = cache

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            return DiggCall(self.endpoint, '.'.join((self.methodname, k)).lstrip('.'), cache=self.cache)

    def __call__(self, **kwargs):
        kwargs['method'] = self.methodname
        kwargs['type'] = 'json'
        kwargs = urlencode(kwargs)

        if self.cache:
            if kwargs in self.cache:
                expires, response = self.cache[kwargs]
                if expires < time():
                    return response
                else:
                    del self.cache[kwargs]

        if self.methodname in POST_ACTIONS:
            # HTTP POST
            req = urllib2.Request('%s?method=%s' % (self.endpoint, self.methodname), kwargs)
            raise NotImplementedError("This method requires OAuth, which hasn't been implemented yet")
        else:
            # HTTP GET
            req = urllib2.Request('%s?%s' % (self.endpoint, kwargs))

        if self.user_agent:
            req.add_header('User-Agent', self.user_agent)
        
        try:
            handle = urllib2.urlopen(req)
            response = json.loads(handle.read())
            if self.cache != None:
                self.update_cache(key=kwargs, value=response, headers=handle.info())
            return response
        except urllib2.HTTPError, e:
            raise DiggError('Digg sent status %i for method: %s\ndetails: %s' % (e.code, self.methodname, e.fp.read()))

    def update_cache(self, key, value, headers):
        cache = True
        expires = int(time()) + 3600

        expires = headers.get('Expires', None)
        if expires:
            expires = mktime(parsedate(expires))
        else:
            expires = int(time()) + 3600

        cache_control = headers.get('Cache-Control', '')
        for control in cache_control.split(','):
            control = control.strip(' ')
            control = control.split('=')
            if len(control) == 2:
                k, v = control
            else:
                k = control
                v = None

            if k in ('private', 'no-cache', 'no-store', 'must-revalidate'):
                cache = False

            if k in ('max-age', 'min-fresh'):
                try:
                    expires = int(time()) + int(v)
                except ValueError:
                    pass

        if cache:
            self.cache[key] = (expires, value)

class Digg(DiggCall):
    def __init__(self, endpoint='http://services.digg.com/1.0/endpoint', user_agent='python-digg/0.1', cache=None):
        DiggCall.__init__(self, endpoint=endpoint, user_agent=user_agent, cache=cache)

__all__ = ['Digg']
