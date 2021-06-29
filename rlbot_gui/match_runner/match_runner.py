from math import pi
from typing import List

import eel
from rlbot.gateway_util import NetworkingRole
from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.matchconfig.match_config import PlayerConfig, MatchConfig, MutatorConfig, ScriptConfig
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.setup_manager import SetupManager, RocketLeagueLauncherPreference
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.game_state_util import GameState, CarState, BallState, Physics, Vector3, Rotator
from rlbot.utils.structures.game_data_struct import GameTickPacket

from rlbot_gui.type_translation.set_state_translation import dict_to_game_state

from rlbot_gui.match_runner.custom_maps import (
    prepare_custom_map,
    identify_map_directory,
    convert_custom_map_to_path
)

sm: SetupManager = None


def create_player_config(bot: dict, human_index_tracker: IncrementingInteger):
    player_config = PlayerConfig()
    player_config.bot = bot['type'] in ('rlbot', 'psyonix')
    player_config.rlbot_controlled = bot['type'] in ('rlbot', 'party_member_bot')
    player_config.bot_skill = bot['skill']
    player_config.human_index = 0 if player_config.bot else human_index_tracker.increment()
    player_config.name = bot['name']
    player_config.team = int(bot['team'])
    if 'path' in bot and bot['path']:
        player_config.config_path = bot['path']
    return player_config

def create_script_config(script):
    return ScriptConfig(script['path'])


def spawn_car_in_showroom(loadout_config: LoadoutConfig, team: int, showcase_type: str, map_name: str,
                          launcher_prefs: RocketLeagueLauncherPreference):
    match_config = MatchConfig()
    match_config.game_mode = 'Soccer'
    match_config.game_map = map_name
    match_config.instant_start = True
    match_config.existing_match_behavior = 'Continue And Spawn'
    match_config.networking_role = NetworkingRole.none
    match_config.enable_state_setting = True
    match_config.skip_replays = True

    bot_config = PlayerConfig()
    bot_config.bot = True
    bot_config.rlbot_controlled = True
    bot_config.team = team
    bot_config.name = "Showroom"
    bot_config.loadout_config = loadout_config

    match_config.player_configs = [bot_config]
    match_config.mutators = MutatorConfig()
    match_config.mutators.boost_amount = 'Unlimited'
    match_config.mutators.match_length = 'Unlimited'

    global sm
    if sm is None:
        sm = SetupManager()
    sm.connect_to_game(launcher_preference=launcher_prefs)
    sm.load_match_config(match_config)
    sm.start_match()

    game_state = GameState(
        cars={0: CarState(physics=Physics(
            location=Vector3(0, 0, 20),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0),
            rotation=Rotator(0, 0, 0)
        ))},
        ball=BallState(physics=Physics(
            location=Vector3(0, 0, -100),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)
        ))
    )
    player_input = PlayerInput()
    team_sign = -1 if team == 0 else 1

    if showcase_type == "boost":
        player_input.boost = True
        player_input.steer = 1
        game_state.cars[0].physics.location.y = -1140
        game_state.cars[0].physics.velocity.x = 2300
        game_state.cars[0].physics.angular_velocity.z = 3.5

    elif showcase_type == "throttle":
        player_input.throttle = 1
        player_input.steer = 0.56
        game_state.cars[0].physics.location.y = -1140
        game_state.cars[0].physics.velocity.x = 1410
        game_state.cars[0].physics.angular_velocity.z = 1.5

    elif showcase_type == "back-center-kickoff":
        game_state.cars[0].physics.location.y = 4608 * team_sign
        game_state.cars[0].physics.rotation.yaw = -0.5 * pi * team_sign

    elif showcase_type == "goal-explosion":
        game_state.cars[0].physics.location.y = -2000 * team_sign
        game_state.cars[0].physics.rotation.yaw = -0.5 * pi * team_sign
        game_state.cars[0].physics.velocity.y = -2300 * team_sign
        game_state.ball.physics.location = Vector3(0, -3500 * team_sign, 93)

    sm.game_interface.update_player_input(player_input, 0)
    sm.game_interface.set_game_state(game_state)


def set_game_state(state):
    global sm
    if sm is None:
        sm = SetupManager()
        sm.connect_to_game()
    game_state = dict_to_game_state(state)
    sm.game_interface.set_game_state(game_state)


def fetch_game_tick_packet() -> GameTickPacket:
    global sm
    if sm is None:
        sm = SetupManager()
        sm.connect_to_game()
    game_tick_packet = GameTickPacket()
    sm.game_interface.update_live_data_packet(game_tick_packet)
    return game_tick_packet


def get_fresh_setup_manager():
    global sm
    if sm is not None:
        try:
            sm.shut_down()
        except Exception as e:
            print(e)
    sm = SetupManager()
    return sm


def setup_match(
    setup_manager: SetupManager, match_config: MatchConfig, launcher_pref: RocketLeagueLauncherPreference
):
    """Starts the match and bots. Also detects and handles custom maps"""

    def do_setup():
        setup_manager.early_start_seconds = 5
        setup_manager.connect_to_game(launcher_preference=launcher_pref)

        # Loading the setup manager's game interface just as a quick fix because story mode uses it. Ideally story mode
        # should now make its own game interface to use.
        setup_manager.game_interface.load_interface(wants_ball_predictions=False, wants_quick_chat=False, wants_game_messages=False)
        setup_manager.load_match_config(match_config)
        setup_manager.launch_early_start_bot_processes()
        setup_manager.start_match()
        setup_manager.launch_bot_processes()
        return setup_manager

    game_map = match_config.game_map
    if game_map.endswith('.upk') or game_map.endswith('.udk'):
        map_file = convert_custom_map_to_path(game_map)
        rl_directory = identify_map_directory(launcher_pref)

        if not all([map_file, rl_directory]):
            print("Couldn't load custom map")
            return

        with prepare_custom_map(map_file, rl_directory) as (game_map, metadata):
            match_config.game_map = game_map
            if "config_path" in metadata:
                config_path = metadata["config_path"]
                match_config.script_configs.append(
                    create_script_config({'path': config_path}))
                print(f"Will load custom script for map {config_path}")
            do_setup()
    else:
        do_setup()


def start_match_helper(bot_list: List[dict], match_settings: dict, launcher_prefs: RocketLeagueLauncherPreference):
    print(bot_list)
    print(match_settings)

    match_config = MatchConfig()
    match_config.game_mode = match_settings['game_mode']
    match_config.game_map = match_settings['map']
    match_config.skip_replays = match_settings['skip_replays']
    match_config.instant_start = match_settings['instant_start']
    match_config.enable_lockstep = match_settings['enable_lockstep']
    match_config.enable_rendering = match_settings['enable_rendering']
    match_config.enable_state_setting = match_settings['enable_state_setting']
    match_config.auto_save_replay = match_settings['auto_save_replay']
    match_config.existing_match_behavior = match_settings['match_behavior']
    match_config.mutators = MutatorConfig()

    mutators = match_settings['mutators']
    match_config.mutators.match_length = mutators['match_length']
    match_config.mutators.max_score = mutators['max_score']
    match_config.mutators.overtime = mutators['overtime']
    match_config.mutators.series_length = mutators['series_length']
    match_config.mutators.game_speed = mutators['game_speed']
    match_config.mutators.ball_max_speed = mutators['ball_max_speed']
    match_config.mutators.ball_type = mutators['ball_type']
    match_config.mutators.ball_weight = mutators['ball_weight']
    match_config.mutators.ball_size = mutators['ball_size']
    match_config.mutators.ball_bounciness = mutators['ball_bounciness']
    match_config.mutators.boost_amount = mutators['boost_amount']
    match_config.mutators.rumble = mutators['rumble']
    match_config.mutators.boost_strength = mutators['boost_strength']
    match_config.mutators.gravity = mutators['gravity']
    match_config.mutators.demolish = mutators['demolish']
    match_config.mutators.respawn_time = mutators['respawn_time']

    human_index_tracker = IncrementingInteger(0)
    match_config.player_configs = [create_player_config(bot, human_index_tracker) for bot in bot_list]
    match_config.script_configs = [create_script_config(script) for script in match_settings['scripts']]

    sm = get_fresh_setup_manager()
    setup_match(sm , match_config, launcher_prefs)
    # Note that we are not calling infinite_loop because that is not compatible with the way eel works!
    # Instead we will reproduce the important behavior from infinite_loop inside this file.

    eel.matchStarted()


def do_infinite_loop_content():
    if sm is not None and sm.has_started:
        sm.try_recieve_agent_metadata()


def hot_reload_bots():
    if sm is not None:
        sm.reload_all_agents()


def shut_down():
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")
