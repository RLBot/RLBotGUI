import os
import webbrowser

import eel
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QFileDialog
from pip._internal import main as pipmain
from rlbot.utils import rate_limiter
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_interface import GameInterface
from rlbot.utils.structures import game_data_struct
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
from rlbot.parsing.match_settings_config_parser import map_types, game_mode_types, \
    boost_amount_mutator_types, match_length_types, max_score_types, overtime_mutator_types, \
    series_length_mutator_types, game_speed_mutator_types, ball_max_speed_mutator_types, ball_type_mutator_types, \
    ball_weight_mutator_types, ball_size_mutator_types, ball_bounciness_mutator_types, rumble_mutator_types, \
    boost_strength_mutator_types, gravity_mutator_types, demolish_mutator_types, respawn_time_mutator_types

from rlbot_gui.bot_management.bot_creation import bootstrap_python_bot
from rlbot_gui.bot_management.downloader import download_and_extract_zip
from rlbot_gui.match_runner.match_runner import hot_reload_bots, shut_down, start_match_helper, do_infinite_loop_content

DEFAULT_BOT_FOLDER = 'default_bot_folder'
settings = QSettings('rlbotgui', 'preferences')


game_tick_packet = None


class GameTickReader:
    def __init__(self):
        self.logger = get_logger('packet reader')
        self.game_interface = GameInterface(self.logger)
        self.game_interface.inject_dll()
        self.game_interface.load_interface()
        self.game_tick_packet = game_data_struct.GameTickPacket()

    def get_packet(self):
        self.game_interface.update_live_data_packet(self.game_tick_packet)
        return self.game_tick_packet


@eel.expose
def start_match(bot_list, match_settings):
    eel.spawn(start_match_helper, bot_list, match_settings)


@eel.expose
def kill_bots():
    shut_down()


@eel.expose
def pick_bot_folder():
    filename = pick_bot_location(True)

    if filename:
        settings.setValue(DEFAULT_BOT_FOLDER, filename)
        settings.sync()
        return scan_for_bots(filename)

    return []


def load_bundle(filename):
    try:
        bundle = get_bot_config_bundle(filename)
        return [{
            'name': bundle.name,
            'type': 'rlbot',
            'image': 'imgs/rlbot.png',
            'path': bundle.config_path,
            'info': read_info(bundle)
        }]
    except Exception as e:
        print(e)

    return []


@eel.expose
def pick_bot_config():
    filename = pick_bot_location(False)
    return load_bundle(filename)


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
        filename, _ = QFileDialog.getOpenFileName(filter="Config files (*.cfg)", options=options)

    app.exit()

    return filename


def read_info(bundle: BotConfigBundle):
    details_header = 'Details'
    if bundle.base_agent_config.has_section(details_header):
        return {
            'developer': bundle.base_agent_config.get(details_header, 'developer'),
            'description': bundle.base_agent_config.get(details_header, 'description'),
            'fun_fact': bundle.base_agent_config.get(details_header, 'fun_fact'),
            'github': bundle.base_agent_config.get(details_header, 'github'),
            'language': bundle.base_agent_config.get(details_header, 'language'),
        }
    return None


@eel.expose
def scan_for_bots(directory):
    bot_directory = directory or settings.value(DEFAULT_BOT_FOLDER, type=str) or "."
    return [
        {
            'name': bundle.name,
            'type': 'rlbot',
            'image': 'imgs/rlbot.png',
            'path': bundle.config_path,
            'info': read_info(bundle)
        }
        for bundle in scan_directory_for_bot_configs(bot_directory)]


@eel.expose
def get_language_support():
    java_return_code = os.system("java -version")
    # Only bother returning iffy languages. No point in sending 'python': True
    return {
        'java': java_return_code == 0,
        'chrome': is_chrome_installed(),  # Scratch bots need chrome to auto-run
    }


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


@eel.expose
def install_package(package_string):
    exit_code = pipmain(['install', package_string])
    print(exit_code)
    return {'exitCode': exit_code, 'package': package_string}


@eel.expose
def download_bot_pack():
    # See https://docs.google.com/document/d/10uCWwHDQYJGMGeoaW1pZu1KvRnSgm064oWL2JVx4k4M/edit?usp=sharing
    # To learn how the bot pack file is hosted and maintained.
    download_and_extract_zip(
        download_url="https://drive.google.com/uc?export=download&id=1OOisnGpxD48x_oAOkBmzqNdkB5POQpiV",
        local_zip_path="RLBotPack.zip", local_folder_path=".")


@eel.expose
def show_bot_in_explorer(bot_cfg_path):
    import subprocess
    directory = os.path.dirname(bot_cfg_path)
    subprocess.Popen(f'explorer "{directory}"')


@eel.expose
def hot_reload_python_bots():
    hot_reload_bots()


@eel.expose
def begin_python_bot(bot_name):

    bot_directory = settings.value(DEFAULT_BOT_FOLDER, type=str) or "."
    config_file = bootstrap_python_bot(bot_name, bot_directory)
    return {'bots': load_bundle(config_file)}


def as_jsonifyable(obj):
    if isinstance(obj, (int, float, str)):
        return obj
    elif "Array" in obj.__class__.__name__:
        return list(map(as_jsonifyable, obj))
    else:
        return {attr: as_jsonifyable(getattr(obj, attr)) for attr in dir(obj) if not attr.startswith("_")}


@eel.expose
def get_game_tick_packet():
    return as_jsonifyable(game_tick_packet)
    

should_quit = False


def on_websocket_close(page, sockets):
    global should_quit
    eel.sleep(3.0)  # We might have just refreshed. Give the websocket a moment to reconnect.
    if not len(eel._websockets):
        # At this point we think the browser window has been closed.
        should_quit = True
        shut_down()


def is_chrome_installed():
    return getattr(eel.browsers, "chm", getattr(eel.browsers, "chr", None)).get_instance_path() is not None


def start():
    webbrowser.open("steam://rungameid/252950")  # Open rocket league if not already opened

    gui_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gui')
    eel.init(gui_folder)

    packet_reader = GameTickReader()
    
    options = {"chromeFlags": ["--autoplay-policy=no-user-gesture-required"]}
    if not is_chrome_installed():
        options = {'mode': 'system-default'}  # Use the system default browser if the user doesn't have chrome.

    # This disable_cache thing only works if you have tare's fork of eel
    # https://github.com/tarehart/Eel/commit/98395ccc268e1a7a5137da2515b472fcc03db5c5
    # installed to pip locally using this technique https://stackoverflow.com/a/49684835
    eel.start('main.html', size=(1000, 800), block=False, callback=on_websocket_close, options=options,
              disable_cache=True)

    while not should_quit:
        global game_tick_packet
        game_tick_packet = packet_reader.get_packet()
        do_infinite_loop_content()
        eel.sleep(1.0)
