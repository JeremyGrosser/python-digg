from urlparse import urlparse, urlunparse
from urllib import urlencode
import urllib2

import oauth2

class SimpleClient(oauth2.Client):
    '''
    Implement an OAuth client on top of python-oauth2 without using httplib2

    Digg's API requires that the User-Agent header be set. This is not normally
    a problem, but their implementation requires that the header key be exactly
    "User-Agent", case sensitive. httplib2's normalize_headers method forces all
    header keys to lower-case for ease of matching in other sections of the
    code. While this is convenient, it completely breaks in situations where
    servers choose to be picky. The authors of httplib2 have acknowledged this
    bug and marked it as wontfix, so we must take matters into our own hands.

    Issue 99: httplib2 should not assume header keys are case-insensitive
    http://code.google.com/p/httplib2/issues/detail?id=99

    This class overrides the request() method of oauth2.Client with a simpler
    implementation that uses Python's builtin urllib2 to perform requests. It
    lacks some of the extra error checking performed by oauth2.Client.request
    but these checks are irrelevant in the context of python-digg, as this
    method only gets called internally.
    '''

    def __init__(self, consumer, token=None):
        oauth2.Client.__init__(self, consumer, token)

    def request(self, uri, method='GET', params={}, headers=None):
        req = oauth2.Request.from_consumer_and_token(self.consumer, token=self.token, http_method=method, http_url=uri, parameters=params)
        req.sign_request(self.method, self.consumer, self.token)

        p = urlparse(uri)
        realm = urlunparse((p.scheme, p.netloc, '/', None, None, None))

        httpreq = urllib2.Request(uri, data=urlencode(params))
        httpreq.add_header('Content-Type', 'application/x-www-form-urlencoded')
        httpreq.add_header(*req.to_header(realm).items()[0])
        return httpreq
