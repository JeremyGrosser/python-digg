from digg.api import Digg
from pprint import pprint

cache = {}
api = Digg(cache=cache)

for story in api.story.getHot()['stories'][:5]:
    print story['title']
    print '%i diggs, %i comments' % (story['diggs'], story['comments'])
    print 'Dugg by', ', '.join([x['user'] for x in api.story.getDiggs(story_id=story['id'])['diggs']]), '\n'
