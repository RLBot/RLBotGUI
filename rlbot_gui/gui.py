from PyQt5.QtWidgets import QApplication, QFileDialog

import eel
from rlbot.matchconfig.match_config import PlayerConfig, MatchConfig, MutatorConfig
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.parsing.match_settings_config_parser import map_types, game_mode_types, \
    boost_amount_mutator_types, match_length_types, max_score_types, overtime_mutator_types, \
    series_length_mutator_types, game_speed_mutator_types, ball_max_speed_mutator_types, ball_type_mutator_types, \
    ball_weight_mutator_types, ball_size_mutator_types, ball_bounciness_mutator_types, rumble_mutator_types, \
    boost_strength_mutator_types, gravity_mutator_types, demolish_mutator_types, respawn_time_mutator_types
from rlbot.setup_manager import SetupManager

sm = None


def create_player_config(bot, human_index_tracker: IncrementingInteger):
    player_config = PlayerConfig()
    player_config.bot = bot['type'] in ('rlbot', 'psyonix')
    player_config.rlbot_controlled = bot['type'] in ('rlbot', 'party_member_bot')
    player_config.bot_skill = 1.0
    player_config.human_index = 0 if player_config.bot else human_index_tracker.increment()
    player_config.name = bot['name']
    player_config.team = int(bot['team'])
    if 'path' in bot and bot['path']:
        player_config.config_path = bot['path']
    return player_config


def start_match_helper(bot_list, match_settings):
    print(bot_list)
    print(match_settings)
    num_participants = len(bot_list)

    match_config = MatchConfig()
    match_config.num_players = num_participants
    match_config.game_mode = match_settings['game_mode']
    match_config.game_map = match_settings['map']
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

    global sm
    if sm is not None:
        try:
            sm.shut_down()
        except Exception as e:
            print(e)

    sm = SetupManager()
    sm.connect_to_game()
    sm.load_match_config(match_config)
    sm.launch_ball_prediction()
    sm.launch_quick_chat_manager()
    sm.launch_bot_processes()
    sm.start_match()
    # Note that we are not calling infinite_loop because that is not compatible with the way eel works!
    # Instead we will reproduce the important behavior from infinite_loop inside this file.


@eel.expose
def start_match(bot_list, match_settings):
    eel.spawn(start_match_helper(bot_list, match_settings))


@eel.expose
def kill_bots():
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")


@eel.expose
def pick_bot_folder():
    filename = pick_bot_location(True)

    if filename:
        return scan_for_bots(filename)

    return []


@eel.expose
def pick_bot_config():
    filename = pick_bot_location(False)

    try:
        bundle = get_bot_config_bundle(filename)
        return [{'name': bundle.name, 'image': 'imgs/rlbot.png', 'path': bundle.config_path}]
    except Exception as e:
        print(e)

    return []


def pick_bot_location(is_folder):
    """
    We're using python for file picking because only python (not javascript) can retrieve
    an actual path on the file system which is what we need.
    https://stackoverflow.com/questions/2809688/directory-chooser-in-html-page

    :return:
    """

    app = QApplication([])
    options = QFileDialog.Options()

    if is_folder:
        filename = QFileDialog.getExistingDirectory(options=options)
    else:
        filename, _ = QFileDialog.getOpenFileName(options=options)  # Or some other dialog

    app.exit()

    return filename


@eel.expose
def scan_for_bots(directory):
    return [{'name': bundle.name, 'type': 'rlbot', 'image': 'imgs/rlbot.png', 'path': bundle.config_path}
            for bundle in scan_directory_for_bot_configs(directory)]


@eel.expose
def get_match_options():
    return {
        'map_types': map_types,
        'game_modes': game_mode_types,
        'mutators': {
            'match_length_types': match_length_types,
            'max_score_types': max_score_types,
            'overtime_types': overtime_mutator_types,
            'series_length_types': series_length_mutator_types,
            'game_speed_types': game_speed_mutator_types,
            'ball_max_speed_types': ball_max_speed_mutator_types,
            'ball_type_types': ball_type_mutator_types,
            'ball_weight_types': ball_weight_mutator_types,
            'ball_size_types': ball_size_mutator_types,
            'ball_bounciness_types': ball_bounciness_mutator_types,
            'boost_amount_types': boost_amount_mutator_types,
            'rumble_types': rumble_mutator_types,
            'boost_strength_types': boost_strength_mutator_types,
            'gravity_types': gravity_mutator_types,
            'demolish_types': demolish_mutator_types,
            'respawn_time_types': respawn_time_mutator_types
        }
    }


should_quit = False


def on_websocket_close(page, sockets):
    global should_quit
    eel.sleep(3.0)  # We might have just refreshed. Give the websocket a moment to reconnect.
    if not len(eel._websockets):
        # At this point we think the browser window has been closed.
        should_quit = True
        if sm is not None:
            sm.shut_down(time_limit=5, kill_all_pids=True)


def start():
    eel.init('gui')
    eel.start('main.html', size=(1000, 800), block=False, callback=on_websocket_close)

    while not should_quit:
        if sm:
            sm.try_recieve_agent_metadata()
        eel.sleep(1.0)
