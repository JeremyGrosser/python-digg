from digg.api import Digg
from pprint import pprint

digg = Digg()
digg.story.getDiggs(count=5, offset=0, story_id=17277750)
