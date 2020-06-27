from functools import lru_cache
from os import path

import json

@lru_cache(maxsize=8)
def read_json(filepath):
    with open(filepath) as fh:
        return json.load(fh)

def get_cities(story_id):
    """
    Get the challenges file specificed by the story_id
    Note: There is no merging with the default story. The challenges file
    must fully specify all challenges
    """
    if isinstance(story_id, str):
        specific_challenges_file = path.join(path.dirname(__file__), f"challenges-{story_id}.json")
    else:
        # custom story
        specific_challenges_file = story_id["challenge"]

    return read_json(specific_challenges_file)["cities"]


def get_challenges_by_id(story_id):
    challenges = get_cities(story_id)
    challenges_by_id = {
        challenge["id"]: challenge for city in challenges.values() for challenge in city["challenges"]
    }
    return challenges_by_id


def get_bots_configs(story_id):
    """
    Get the base bots config and merge it with bots-{story_id}.json
    """
    specific_bots_file = ''
    if isinstance(story_id, str):
        specific_bots_file = path.join(path.dirname(__file__), f"bots-{story_id}.json")
    elif "bots" in story_id and story_id["bots"]:
        specific_bots_file = story_id["bots"]

    base_bots_file = path.join(path.dirname(__file__), f"challenges-default.json")

    bots: dict = read_json(base_bots_file)["bots"]
    if path.exists(specific_bots_file):
        bots.update(read_json(specific_bots_file)["bots"])

    return bots
