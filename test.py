from urlparse import parse_qs
import sys

from digg.api import Digg

#import memcache
#cache = memcache.Client(['127.0.0.1:11211'])
#digg = Digg(oauth_consumer=consumer, cache=cache)

def test_story():
    digg = Digg()
    for story in digg.story.getHot()['stories']:
        print story['title']
        print '%i diggs, %i comments' % (story['diggs'], story['comments'])
        print 'Dugg by', ', '.join([x['user'] for x in digg.story.getDiggs(story_id=story['id'])['diggs']]), '\n'

def test_oauth():
    from oauth2 import Consumer, Token
    consumer = Consumer(key='7c26730528d8cf0b3b5c7f0477060c00', secret='toomanysecrets')
    digg = Digg(oauth_consumer=consumer)

    response = digg.oauth.getRequestToken(oauth_callback='oob')
    request_token = parse_qs(response)
    print 'Got request token!'
    print 'Go to the following URL to authorize this application'
    print 'http://digg.com/oauth/authorize?oauth_token=%s' % request_token['oauth_token'][0]

    sys.stdout.write('Type the verification number: ')
    verifier = sys.stdin.readline().rstrip('\r\n')

    request_token = Token(request_token['oauth_token'][0], request_token['oauth_token_secret'][0])
    request_token.set_verifier(verifier)
    response = digg.oauth.getAccessToken(oauth_token=request_token)
    response = parse_qs(response)
    access_token = Token(response['oauth_token'][0], response['oauth_token_secret'][0])
    print 'Got access token!'

    print digg.oauth.verify(oauth_token=access_token)
    print 'OAuth verification successful!'

if __name__ == '__main__':
    #test_story()
    test_oauth()
