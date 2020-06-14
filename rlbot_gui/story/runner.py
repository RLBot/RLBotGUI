"""
Manages the story
"""
import eel

from PyQt5.QtCore import QSettings

from rlbot.setup_manager import SetupManager
from rlbot.parsing.match_settings_config_parser import (
    boost_amount_mutator_types,
    map_types,
    game_mode_types,
    match_length_types,
    max_score_types,
    overtime_mutator_types,
    series_length_mutator_types,
    game_speed_mutator_types,
    ball_max_speed_mutator_types,
    ball_type_mutator_types,
    ball_weight_mutator_types,
    ball_size_mutator_types,
    ball_bounciness_mutator_types,
    rumble_mutator_types,
    boost_strength_mutator_types,
    gravity_mutator_types,
    demolish_mutator_types,
    respawn_time_mutator_types,
    existing_match_behavior_types,
)
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.matchconfig.loadout_config import Color, LoadoutConfig
from rlbot.matchconfig.match_config import (
    PlayerConfig,
    MatchConfig,
    MutatorConfig,
    ScriptConfig,
)

from rlbot.utils.game_state_util import GameState, CarState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from rlbot_gui.match_runner.match_runner import (
    create_player_config,
    create_script_config,
)

CURRENT_STATE = None

##### EEL -- these are the hooks exposed to JS
@eel.expose
def story_story_test():
    print("In story_story_test()")
    eel.spawn(story_test)

@eel.expose
def story_load_save():
    """Loads a previous save if available."""
    global CURRENT_STATE
    settings = QSettings('rlbotgui', 'story_save')
    state = settings.value("save")
    if state:
        print(f"Save state: {state}")
        CURRENT_STATE = StoryState.from_dict(state)
    return state

@eel.expose
def story_new_save(name, color_secondary):
    global CURRENT_STATE
    CURRENT_STATE = StoryState.new(name, color_secondary)
    return story_save_state()


@eel.expose
def story_delete_save():
    global CURRENT_STATE
    CURRENT_STATE = None
    QSettings('rlbotgui', 'story_save').remove("save")


@eel.expose
def story_save_state():
    settings = QSettings('rlbotgui', 'story_save')
    serialized = CURRENT_STATE.__dict__
    settings.setValue("save", serialized)
    return serialized

@eel.expose
def launch_challenge(challenge_id):
    if challenge_id == "INTRO-1":
        launch_intro_1()



sm: SetupManager = None
STARTING_BOT_POOL = [
    {
        "name": "Human",
        "type": "human",
        "image": "imgs/human.png",
        "skill": 1,
    },
    {
        "name": "Psyonix Allstar",
        "type": "psyonix",
        "skill": 1,
        "image": "imgs/psyonix.png",
    },
    {
        "name": "Psyonix Pro",
        "type": "psyonix",
        "skill": 0.5,
        "image": "imgs/psyonix.png",
    },
    {
        "name": "Psyonix Rookie",
        "type": "psyonix",
        "skill": 0,
        "image": "imgs/psyonix.png",
    },
]

NON_PSYONIX_BOTS = [
    {
        "name": "Self-driving car",
        "type": "rlbot",
        "skill": 1,
        "path": "C:\\Users\\Triton\\Projects\\RLBotGUI\\RLBotPackDeletable\\RLBotPack-master\\RLBotPack\\Self-driving car\\self-driving-car.cfg",
    },
    {
        "name": "ReliefBot",
        "type": "rlbot",
        "skill": 1,
        "path": "C:\\Users\\Triton\\Projects\\RLBotGUI\\RLBotPackDeletable\\RLBotPack-master\\RLBotPack\\ReliefBotFamily\\README\\relief_bot.cfg",
    },
]



def start_match_helper(player_configs, match_settings):
    # print(bot_list)
    print(match_settings)

    match_config = MatchConfig()
    match_config.game_mode = match_settings["game_mode"]
    match_config.game_map = match_settings["map"]
    match_config.skip_replays = match_settings["skip_replays"]
    match_config.instant_start = match_settings["instant_start"]
    match_config.enable_lockstep = match_settings["enable_lockstep"]
    match_config.enable_rendering = match_settings["enable_rendering"]
    match_config.enable_state_setting = match_settings["enable_state_setting"]
    match_config.auto_save_replay = match_settings["auto_save_replay"]
    match_config.existing_match_behavior = match_settings["match_behavior"]
    match_config.mutators = MutatorConfig()

    mutators = match_settings["mutators"]
    match_config.mutators.match_length = mutators["match_length"]
    match_config.mutators.max_score = mutators["max_score"]
    match_config.mutators.overtime = mutators["overtime"]
    match_config.mutators.series_length = mutators["series_length"]
    match_config.mutators.game_speed = mutators["game_speed"]
    match_config.mutators.ball_max_speed = mutators["ball_max_speed"]
    match_config.mutators.ball_type = mutators["ball_type"]
    match_config.mutators.ball_weight = mutators["ball_weight"]
    match_config.mutators.ball_size = mutators["ball_size"]
    match_config.mutators.ball_bounciness = mutators["ball_bounciness"]
    match_config.mutators.boost_amount = mutators["boost_amount"]
    match_config.mutators.rumble = mutators["rumble"]
    match_config.mutators.boost_strength = mutators["boost_strength"]
    match_config.mutators.gravity = mutators["gravity"]
    match_config.mutators.demolish = mutators["demolish"]
    match_config.mutators.respawn_time = mutators["respawn_time"]

    match_config.player_configs = player_configs
    match_config.script_configs = [
        create_script_config(script) for script in match_settings["scripts"]
    ]

    global sm
    if sm is not None:
        try:
            sm.shut_down()
        except Exception as e:
            print(e)

    sm = SetupManager()
    sm.early_start_seconds = 5
    sm.connect_to_game()
    sm.load_match_config(match_config)
    sm.launch_early_start_bot_processes()
    sm.start_match()
    sm.launch_bot_processes()
    # Note that we are not calling infinite_loop because that is not compatible with the way eel works!
    # Instead we will reproduce the important behavior from infinite_loop inside this file.

    return sm


class StoryState:
    """Represents users game state"""

    def __init__(self):
        self.version = 1
        self.team_info = {"name": "", "color_secondary": ""}
        self.teammates = []
        self.cities = []

    @staticmethod
    def new(name, color_secondary):
        s = StoryState()
        s.team_info = {
            "name": name,
            "color_secondary": color_secondary
        }
        return s

    @staticmethod
    def from_dict(source):
        """No validation done here."""
        s = StoryState()
        s.__dict__.update(source)


def launch_intro_1():
    print("In launch_intro_1")

    human_index_tracker = IncrementingInteger(0)
    players = [STARTING_BOT_POOL[0], STARTING_BOT_POOL[1].copy()]
    players[0]["team"] = 0
    players[1]["team"] = 1
    match_players = [
        create_player_config(bot, human_index_tracker) for bot in players
    ]

    match_settings = {
        "game_mode": game_mode_types[0],
        "map": map_types[0],
        "skip_replays": False,
        "instant_start": False,
        "enable_lockstep": False,
        "enable_state_setting": True,
        "enable_rendering": False,
        "auto_save_replay": False,
        "match_behavior": existing_match_behavior_types[0],
        "mutators": {
            "match_length": match_length_types[0],
            "max_score": max_score_types[0],  # 1 goal max
            "overtime": overtime_mutator_types[0],
            "series_length": series_length_mutator_types[0],
            "game_speed": game_speed_mutator_types[0],
            "ball_max_speed": ball_max_speed_mutator_types[0],
            "ball_type": ball_type_mutator_types[0],
            "ball_weight": ball_weight_mutator_types[0],
            "ball_size": ball_size_mutator_types[0],
            "ball_bounciness": ball_bounciness_mutator_types[0],
            "boost_amount": boost_amount_mutator_types[0],
            "rumble": rumble_mutator_types[0],
            "boost_strength": boost_strength_mutator_types[0],
            "gravity": gravity_mutator_types[0],
            "demolish": demolish_mutator_types[0],
            "respawn_time": respawn_time_mutator_types[0],
        },
        "scripts": [],
    }
    setup_manager = start_match_helper(match_players, match_settings)

    while True:
        eel.sleep(1.0 / 120)  # does RL support faster?
        game_tick_packet = GameTickPacket()
        packet = setup_manager.game_interface.fresh_live_data_packet(
            game_tick_packet, 1000, 324532
        )

        game_state = GameState.create_from_gametickpacket(packet)
        changed = False
        for _, car in game_state.cars.items():
            if car.boost_amount > 0:
                car.boost_amount = 0
                changed = True
            # if car.jumped:
            #     car.double_jumped = True
            #     changed = True

        if changed:
            setup_manager.game_interface.set_game_state(game_state)
        # print([t.score for t in packet.teams])
        if packet.game_info.is_match_ended:
            print("Donezo")
            #TODO: UPDATE STATE!
            break


def story_test():
    print("In story_test")

    human_index_tracker = IncrementingInteger(0)
    players = [STARTING_BOT_POOL[0], NON_PSYONIX_BOTS[1].copy()]
    players[0]["team"] = 0
    players[1]["team"] = 0
    players.extend(NON_PSYONIX_BOTS)
    players[2]["team"] = 1
    players[3]["team"] = 1
    match_players = [
        create_player_config(bot, human_index_tracker) for bot in players
    ]
    for player in match_players:
        if player.loadout_config is None:
            print("Creating fresh loadout for player.name")
            player.loadout_config = LoadoutConfig()
        player.loadout_config.primary_color_lookup = Color(0, 0, 0, 255)
        player.loadout_config.secondary_color_lookup = Color(50, 220, 255, 255)

    match_settings = {
        "game_mode": game_mode_types[0],
        "map": map_types[0],
        "skip_replays": False,
        "instant_start": False,
        "enable_lockstep": False,
        "enable_state_setting": True,
        "enable_rendering": False,
        "auto_save_replay": False,
        "match_behavior": existing_match_behavior_types[0],
        "mutators": {
            "match_length": match_length_types[0],
            "max_score": max_score_types[1],  # 1 goal max
            "overtime": overtime_mutator_types[0],
            "series_length": series_length_mutator_types[0],
            "game_speed": game_speed_mutator_types[0],
            "ball_max_speed": ball_max_speed_mutator_types[0],
            "ball_type": ball_type_mutator_types[0],
            "ball_weight": ball_weight_mutator_types[0],
            "ball_size": ball_size_mutator_types[0],
            "ball_bounciness": ball_bounciness_mutator_types[0],
            "boost_amount": boost_amount_mutator_types[0],
            "rumble": rumble_mutator_types[0],
            "boost_strength": boost_strength_mutator_types[0],
            "gravity": gravity_mutator_types[0],
            "demolish": demolish_mutator_types[0],
            "respawn_time": respawn_time_mutator_types[0],
        },
        "scripts": [],
    }
    setup_manager = start_match_helper(match_players, match_settings)

    while True:
        eel.sleep(1.0 / 120)  # does RL support faster?
        game_tick_packet = GameTickPacket()
        packet = setup_manager.game_interface.fresh_live_data_packet(
            game_tick_packet, 1000, 324532
        )

        game_state = GameState.create_from_gametickpacket(packet)
        changed = False
        # for _, car in game_state.cars.items():
        car = game_state.cars[0]
        if car.boost_amount > 0:
            car.boost_amount = 0
            changed = True
            # if car.jumped:
            #     car.double_jumped = True
            #     changed = True

        if changed:
            setup_manager.game_interface.set_game_state(game_state)
        # print([t.score for t in packet.teams])
        if packet.game_info.is_match_ended:
            print("Donezo")
            break
