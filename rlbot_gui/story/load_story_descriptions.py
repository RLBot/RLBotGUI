
from os import path

import json

BOTS_CONFIG = None
CHALLENGES = None
CHALLENGES_BY_ID = None

# BOTS
with open(path.join(path.dirname(__file__), "bots.json")) as botlist:
    BOTS_CONFIG = json.load(botlist)

# CHALLENGES
with open(path.join(path.dirname(__file__), 'challenges.json')) as c:
    CHALLENGES = json.load(c)
    CHALLENGES_BY_ID = {
        challenge["id"]: challenge 
        for city in CHALLENGES.values() for challenge in city }