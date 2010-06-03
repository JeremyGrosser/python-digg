from digg.api import Digg
from pprint import pprint

api = Digg()

for story in api.story.getHot()['stories']:
    print story['title']
    print '%i diggs, %i comments' % (story['diggs'], story['comments'])
    print 'Dugg by', ', '.join([x['user'] for x in api.story.getDiggs(story_id=story['id'])['diggs']]), '\n'
