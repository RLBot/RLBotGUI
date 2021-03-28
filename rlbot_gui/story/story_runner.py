"""
Manages the story
"""
from datetime import datetime
import json
from os import path

import eel
from PyQt5.QtCore import QSettings

from rlbot_gui.persistence.settings import load_launcher_settings, launcher_preferences_from_map
from rlbot_gui.story.story_challenge_setup import run_challenge, configure_challenge
from rlbot_gui.story.load_story_descriptions import (
    get_bots_configs,
    get_cities,
    get_story_settings,
    get_challenges_by_id,
    get_scripts_configs
)


CURRENT_STATE = None

##### EEL -- these are the hooks exposed to JS
@eel.expose
def story_story_test():
    print("In story_story_test()")
    # easy way to trigger python code


@eel.expose
def get_cities_json(story_id):
    return get_cities(story_id)


@eel.expose
def get_bots_json(story_id):
    return get_bots_configs(story_id)

@eel.expose
def get_story_settings_json(story_id):
    return get_story_settings(story_id)


@eel.expose
def story_load_save():
    """Loads a previous save if available."""
    global CURRENT_STATE
    settings = QSettings("rlbotgui", "story_save")
    state = settings.value("save")
    if state:
        print(f"Save state: {state}")
        CURRENT_STATE = StoryState.from_dict(state)
        # default values should get added if missing
        state = CURRENT_STATE.__dict__
    return state


@eel.expose
def story_new_save(player_settings, story_settings):
    global CURRENT_STATE
    CURRENT_STATE = StoryState.new(player_settings, story_settings)
    return story_save_state()


@eel.expose
def story_delete_save():
    global CURRENT_STATE
    CURRENT_STATE = None
    QSettings("rlbotgui", "story_save").remove("save")


@eel.expose
def story_save_state():
    settings = QSettings("rlbotgui", "story_save")
    serialized = CURRENT_STATE.__dict__
    settings.setValue("save", serialized)
    return serialized


@eel.expose
def story_save_fake_state(state):
    """Only use for debugging.
    Normally state should just flow from python to JS"""
    global CURRENT_STATE
    settings = QSettings("rlbotgui", "story_save")
    CURRENT_STATE = CURRENT_STATE.from_dict(state)
    settings.setValue("save", state)


@eel.expose
def launch_challenge(challenge_id, pickedTeammates):
    launch_challenge_with_config(challenge_id, pickedTeammates)


@eel.expose
def purchase_upgrade(id, current_currency, cost):
    CURRENT_STATE.add_purchase(id, current_currency, cost)
    flush_save_state()


@eel.expose
def recruit(id, current_currency):
    CURRENT_STATE.add_recruit(id, current_currency)
    flush_save_state()


##### Reverse eel's


def flush_save_state():
    serialized = story_save_state()
    eel.loadUpdatedSaveState(serialized)


#################################


class StoryState:
    """Represents users game state"""

    def __init__(self):
        self.version = 1
        self.story_config = "default" # can be dict for custom config
        self.team_info = {"name": "", "color_secondary": ""}
        self.teammates = []
        self.challenges_attempts = {}  # many entries per challenge
        self.challenges_completed = {}  # one entry per challenge

        self.upgrades = {"currency": 0}

    def add_purchase(self, id, current_currency, cost):
        """The only validation we do is to make sure current_currency is correct.
        This is NOT a security mechanism, this is a bug prevention mechanism to
        avoid accidental double clicks.
        """
        if self.upgrades["currency"] == current_currency:
            self.upgrades[id] = True
            self.upgrades["currency"] -= cost

    def add_recruit(self, id, current_currency):
        """The only validation we do is to make sure current_currency is correct.
        This is NOT a security mechanism, this is a bug prevention mechanism to
        avoid accidental double clicks.
        """
        if self.upgrades["currency"] == current_currency:
            self.teammates.append(id)
            self.upgrades["currency"] -= 1

    def add_match_result(
        self, challenge_id: str, challenge_completed: bool, game_results
    ):
        """game_results should be the output of packet_to_game_results.
        You have to call it anyways to figure out if the player
        completed the challenge so that's why we don't call it again here.
        """
        if challenge_id not in self.challenges_attempts:
            # no defaultdict because we serialize the data
            self.challenges_attempts[challenge_id] = []

        self.challenges_attempts[challenge_id].append(
            {"game_results": game_results, "challenge_completed": challenge_completed}
        )

        if challenge_completed:
            index = len(self.challenges_attempts[challenge_id]) - 1
            self.challenges_completed[challenge_id] = index
            self.upgrades["currency"] += 2

    @staticmethod
    def new(player_settings, story_settings):
        s = StoryState()

        name = player_settings["name"]
        color_secondary = player_settings["color"]
        s.team_info = {"name": name, "color_secondary": color_secondary}

        story_id = story_settings["story_id"]
        custom_config = story_settings["custom_config"]
        use_custom_maps = story_settings["use_custom_maps"]
        if story_id == 'custom':
            s.story_config = custom_config
        else:
            s.story_config = story_id
            if use_custom_maps:
                s.story_config = f"{story_id}-with-cmaps"
        return s

    @staticmethod
    def from_dict(source):
        """No validation done here."""
        s = StoryState()
        s.__dict__.update(source)
        return s


def launch_challenge_with_config(challenge_id, pickedTeammates):
    print(f"In launch_challenge {challenge_id}")

    story_id = CURRENT_STATE.story_config
    challenge = get_challenges_by_id(story_id)[challenge_id]
    all_bots = get_bots_configs(story_id)
    all_scripts = get_scripts_configs(story_id)


    match_config = configure_challenge(challenge, CURRENT_STATE, pickedTeammates, all_bots, all_scripts)
    launcher_settings_map = load_launcher_settings()
    launcher_prefs = launcher_preferences_from_map(launcher_settings_map)
    completed, results = run_challenge(match_config, challenge, CURRENT_STATE.upgrades, launcher_prefs)
    CURRENT_STATE.add_match_result(challenge_id, completed, results)

    flush_save_state()
