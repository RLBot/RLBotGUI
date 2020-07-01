from functools import lru_cache
from os import path
from copy import deepcopy

import json

@lru_cache(maxsize=8)
def read_json(filepath):
    with open(filepath) as fh:
        return json.load(fh)


def story_id_to_file(story_id):
    if isinstance(story_id, str):
        filepath = path.join(path.dirname(__file__), f"story-{story_id}.json")
    else:
        # custom story
        filepath = story_id["storyPath"]

    return filepath 


def get_cities(story_id):
    """
    Get the challenges file specificed by the story_id
    Note: There is no merging with the default story. The story file
    must fully specify all challenges and cities
    """
    specific_challenges_file = story_id_to_file(story_id)

    return read_json(specific_challenges_file)["cities"]


def get_challenges_by_id(story_id):
    cities = get_cities(story_id)
    challenges_by_id = { }
    for city_id, city in cities.items():
        for challenge in  city["challenges"]:
            challenges_by_id[challenge["id"]] = deepcopy(challenge)
            challenges_by_id[challenge["id"]]["city_description"] = city["description"]
    return challenges_by_id


def get_bots_configs(story_id):
    """
    Get the base bots config and merge it with the bots in the
    story config
    """
    specific_bots_file = story_id_to_file(story_id)
    base_bots_file = path.join(path.dirname(__file__), f"bots-base.json")

    bots: dict = read_json(base_bots_file)
    if path.exists(specific_bots_file):
        bots.update(read_json(specific_bots_file)["bots"])

    return bots
