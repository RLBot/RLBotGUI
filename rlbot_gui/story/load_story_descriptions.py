from functools import lru_cache
from os import path

import json

def read_json(filepath):
    with open(filepath) as fh:
        return json.load(fh)

@lru_cache(maxsize=4)
def get_challenges(story_id: str):
    """
    Get the challenges file specificed by the story_id
    Note: There is no merging with the default story. The challenges file
    must fully specify all challenges
    """
    if story_id.startswith('CUSTOM:'):
        # figure out how custom loading works
        raise NotImplementedError("CUSTOM story loading not implemented yet")
    else:
        specific_challenges_file = path.join(path.dirname(__file__), f"challenges-{story_id}.json")

    return read_json(specific_challenges_file)


@lru_cache(maxsize=4)
def get_challenges_by_id(story_id):
    challenges = get_challenges(story_id)
    challenges_by_id = {
        challenge["id"]: challenge for city in challenges.values() for challenge in city
    }
    return challenges_by_id


@lru_cache(maxsize=4)
def get_bots_configs(story_id):
    """
    Get the base bots config and merge it with bots-{story_id}.json
    """
    if story_id.startswith('CUSTOM:'):
        # figure out how custom loading works
        raise NotImplementedError("CUSTOM story loading not implemented yet")
    else:
        base_bots_file = path.join(path.dirname(__file__), f"bots-base.json")
        specific_bots_file = path.join(path.dirname(__file__), f"bots-{story_id}.json")

        bots: dict = read_json(base_bots_file)
        if path.exists(specific_bots_file):
            bots.update(read_json(specific_bots_file))

        return bots
