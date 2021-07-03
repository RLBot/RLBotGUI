import os
import shutil
import subprocess
import sys
import json
from pathlib import Path

import eel
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QFileDialog
from rlbot.parsing.agent_config_parser import create_looks_configurations, BOT_CONFIG_LOADOUT_HEADER, \
    BOT_CONFIG_LOADOUT_ORANGE_HEADER, BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER, BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER, \
    load_bot_appearance
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, get_script_config_bundle, RunnableConfigBundle, \
    BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs, scan_directory_for_script_configs
from rlbot.parsing.match_settings_config_parser import map_types, game_mode_types, \
    boost_amount_mutator_types, match_length_types, max_score_types, overtime_mutator_types, \
    series_length_mutator_types, game_speed_mutator_types, ball_max_speed_mutator_types, ball_type_mutator_types, \
    ball_weight_mutator_types, ball_size_mutator_types, ball_bounciness_mutator_types, rumble_mutator_types, \
    boost_strength_mutator_types, gravity_mutator_types, demolish_mutator_types, respawn_time_mutator_types, \
    existing_match_behavior_types
from rlbot.setup_manager import SetupManager
from rlbot.utils.requirements_management import install_requirements_file

from rlbot_gui.bot_management.bot_creation import bootstrap_python_bot, bootstrap_scratch_bot, \
    bootstrap_python_hivemind, convert_to_filename
from rlbot_gui.bot_management.downloader import BotpackStatus, RepoDownloader, BotpackUpdater, get_json_from_url, \
    MapPackUpdater
from rlbot_gui.match_runner.match_runner import hot_reload_bots, shut_down, start_match_helper, \
    do_infinite_loop_content, spawn_car_in_showroom, set_game_state, fetch_game_tick_packet
from rlbot_gui.match_runner.custom_maps import find_all_custom_maps
from rlbot_gui.type_translation.packet_translation import convert_packet_to_dict
from rlbot_gui.persistence.settings import load_settings, BOT_FOLDER_SETTINGS_KEY, MATCH_SETTINGS_KEY, \
    LAUNCHER_SETTINGS_KEY, TEAM_SETTINGS_KEY, load_launcher_settings, launcher_preferences_from_map
from rlbot import gateway_util

#### LOAD JUST TO EXPOSE STORY_MODE
from rlbot_gui.story import story_runner
####

DEFAULT_BOT_FOLDER = 'default_bot_folder'
BOTPACK_FOLDER = 'RLBotPackDeletable'
MAPPACK_FOLDER = 'RLBotMapPackDeletable'
MAPPACK_REPO = ("azeemba", "RLBotMapPack")
OLD_BOTPACK_FOLDER = 'RLBotPack'
BOTPACK_REPO_OWNER = 'RLBot'
BOTPACK_REPO_NAME = 'RLBotPack'
BOTPACK_REPO_BRANCH = 'master' # can't change with the new release system
CREATED_BOTS_FOLDER = 'MyBots'
COMMIT_ID_KEY = 'latest_botpack_commit_id'
bot_folder_settings = None


@eel.expose
def start_match(bot_list, match_settings):
    launcher_preference_map = load_launcher_settings()
    launcher_prefs = launcher_preferences_from_map(launcher_preference_map)

    # Show popup in GUI if rocket league is not started with -rlbot flag
    try:
        testSetupManager = SetupManager()
        temp, port = gateway_util.find_existing_process()
        del temp
        testSetupManager.is_rocket_league_running(port);
    except Exception:
        eel.noRLBotFlagPopup()
        print("Error starting match. This is probably due to Rocket League not being started under the -rlbot flag.")
    else:
        eel.spawn(start_match_helper, bot_list, match_settings, launcher_prefs)


@eel.expose
def kill_bots():
    shut_down()


@eel.expose
def pick_bot_folder():
    filename = pick_location(True)

    if filename:
        global bot_folder_settings
        bot_folder_settings['folders'][filename] = {'visible': True}
        settings = load_settings()
        settings.setValue(DEFAULT_BOT_FOLDER, filename)
        settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
        settings.sync()
        return scan_for_bots()

    return []


def serialize_bundle(bundle: BotConfigBundle):
    return {
        'name': bundle.name,
        'type': 'rlbot',
        'skill': 1,
        'image': 'imgs/rlbot.png',
        'path': bundle.config_path,
        'looks_path': bundle.looks_path,
        'info': read_info(bundle),
        'logo': try_copy_logo(bundle),
        'missing_python_packages': [r.line for r in bundle.get_missing_python_packages() + bundle.get_python_packages_needing_upgrade()],
    }


def serialize_script_bundle(bundle):
    return {
        'name': bundle.name,
        'type': 'script',
        'image': 'imgs/rlbot.png',
        'path': bundle.config_path,
        'info': read_info(bundle),
        'logo': try_copy_logo(bundle),
        'missing_python_packages': [r.line for r in bundle.get_missing_python_packages() + bundle.get_python_packages_needing_upgrade()],
    }


def load_bot_bundle(filename):
    try:
        bundle = get_bot_config_bundle(filename)
        return [serialize_bundle(bundle)]
    except Exception as e:
        print(e)

    return []


def load_script_bundle(filename):
    try:
        bundle = get_script_config_bundle(filename)
        return [serialize_script_bundle(bundle)]
    except Exception as e:
        print(e)

    return []


@eel.expose
def pick_bot_config():
    filename = pick_location(False)
    bundle = load_script_bundle(filename) or load_bot_bundle(filename)

    if bundle:
        bot_folder_settings["files"][filename] = {"visible": True}
        settings = QSettings("rlbotgui", "preferences")
        settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
        settings.sync()

    return bundle


@eel.expose
def get_folder_settings():
    return bot_folder_settings


@eel.expose
def save_folder_settings(folder_settings):
    global bot_folder_settings
    bot_folder_settings = folder_settings
    settings = QSettings('rlbotgui', 'preferences')
    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.sync()


def validate_bots(bots):
    '''Reload rlbot controlled bot bundles and remove invalid ones'''
    valid_bots = []

    for bot in bots:
        if bot["type"] in ('rlbot', 'party_member_bot'):
            valid_bots += load_bot_bundle(bot["path"])
        else:
            valid_bots.append(bot)

    return valid_bots


@eel.expose
def get_match_settings():
    settings = load_settings()
    match_settings = settings.value(MATCH_SETTINGS_KEY, type=dict)
    return match_settings if match_settings else None


@eel.expose
def get_launcher_settings():
    return load_launcher_settings()


@eel.expose
def get_team_settings():
    settings = load_settings()
    team_settings = settings.value(TEAM_SETTINGS_KEY, type=dict)
    if not team_settings:
        return None

    return {
        "blue_team": validate_bots(team_settings["blue_team"]),
        "orange_team": validate_bots(team_settings["orange_team"])
    }


@eel.expose
def save_match_settings(match_settings):
    settings = load_settings()
    settings.setValue(MATCH_SETTINGS_KEY, match_settings)


@eel.expose
def save_launcher_settings(launcher_settings_map):
    settings = load_settings()
    settings.setValue(LAUNCHER_SETTINGS_KEY, launcher_settings_map)


@eel.expose
def save_team_settings(blue_bots, orange_bots):
    settings = load_settings()
    settings.setValue(TEAM_SETTINGS_KEY, {"blue_team": blue_bots, "orange_team": orange_bots})


@eel.expose
def pick_location(is_folder, filter="Config files (*.cfg)"):
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
        filename, _ = QFileDialog.getOpenFileName(filter=filter, options=options)

    app.exit()

    return filename


def read_info(bundle: RunnableConfigBundle):
    details_header = 'Details'
    if bundle.base_agent_config.has_section(details_header):
        raw_tags = bundle.base_agent_config.get(details_header, 'tags')
        return {
            'developer': bundle.base_agent_config.get(details_header, 'developer'),
            'description': bundle.base_agent_config.get(details_header, 'description'),
            'fun_fact': bundle.base_agent_config.get(details_header, 'fun_fact'),
            'github': bundle.base_agent_config.get(details_header, 'github'),
            'language': bundle.base_agent_config.get(details_header, 'language'),
            'tags': [tag.strip() for tag in raw_tags.split(',')] if raw_tags else [],
        }
    return None


@eel.expose
def get_looks(path: str) -> dict:
    looks_config = create_looks_configurations().parse_file(path)
    looks = {'blue': {}, 'orange': {}}

    def serialize_category(target: dict, header_name: str):
        header = looks_config.get_header(header_name)
        for key in header.values.keys():
            if header.get(key) is not None:
                target[key] = str(header.get(key))

    serialize_category(looks['blue'], BOT_CONFIG_LOADOUT_HEADER)
    serialize_category(looks['orange'], BOT_CONFIG_LOADOUT_ORANGE_HEADER)
    serialize_category(looks['blue'], BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER)
    serialize_category(looks['orange'], BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER)

    return looks


def convert_to_looks_config(looks: dict):
    looks_config = create_looks_configurations()

    def deserialize_category(source: dict, header_name: str):
        header = looks_config.get_header(header_name)
        for key in header.values.keys():
            if key in source:
                header.set_value(key, source[key])

    deserialize_category(looks['blue'], BOT_CONFIG_LOADOUT_HEADER)
    deserialize_category(looks['orange'], BOT_CONFIG_LOADOUT_ORANGE_HEADER)
    deserialize_category(looks['blue'], BOT_CONFIG_LOADOUT_PAINT_BLUE_HEADER)
    deserialize_category(looks['orange'], BOT_CONFIG_LOADOUT_PAINT_ORANGE_HEADER)

    return looks_config


@eel.expose
def save_looks(looks: dict, path: str):
    looks_config = convert_to_looks_config(looks)

    with open(path, 'w', encoding='utf8') as f:
        f.write(str(looks_config))
        print(f'Saved appearance to {path}')


@eel.expose
def spawn_car_for_viewing(looks: dict, team: int, showcase_type: str, map_name: str):
    looks_config = convert_to_looks_config(looks)
    loadout_config = load_bot_appearance(looks_config, team)
    launcher_settings_map = get_launcher_settings()
    launcher_prefs = launcher_preferences_from_map(launcher_settings_map)
    spawn_car_in_showroom(loadout_config, team, showcase_type, map_name, launcher_prefs)


@eel.expose
def scan_for_bots():
    bot_hash = {}

    for folder, props in bot_folder_settings['folders'].items():
        if props['visible']:
            bots = get_bots_from_directory(folder)
            for bot in bots:
                bot_hash[bot['path']] = bot

    for file, props in bot_folder_settings['files'].items():
        if props['visible']:
            bots = load_bot_bundle(file)  # Returns a list of size 1
            for bot in bots:
                bot_hash[bot['path']] = bot

    return list(bot_hash.values())


@eel.expose
def scan_for_scripts():
    script_hash = {}

    for folder, props in bot_folder_settings['folders'].items():
        if props['visible']:
            bots = get_scripts_from_directory(folder)
            for bot in bots:
                script_hash[bot['path']] = bot

    for file, props in bot_folder_settings['files'].items():
        if props['visible']:
            bots = load_script_bundle(file)  # Returns a list of size 1
            for bot in bots:
                script_hash[bot['path']] = bot

    return list(script_hash.values())


def try_copy_logo(bundle: RunnableConfigBundle):
    logo_path = bundle.get_logo_file()
    if logo_path is not None and os.path.exists(logo_path):
        web_url = 'imgs/logos/' + convert_to_filename(bundle.name) + '/' + convert_to_filename(logo_path)
        target_file = os.path.join(os.path.dirname(__file__), 'gui', web_url)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        shutil.copy(logo_path, target_file)
        return web_url
    return None


def get_bots_from_directory(bot_directory):
    bundles = filter_hidden_bundles(scan_directory_for_bot_configs(bot_directory))
    return [serialize_bundle(bundle) for bundle in bundles]


def get_scripts_from_directory(bot_directory):
    bundles = filter_hidden_bundles(scan_directory_for_script_configs(bot_directory))
    return [serialize_script_bundle(bundle) for bundle in bundles]


def filter_hidden_bundles(bundles):
    return [bundle for bundle in bundles if not bundle.config_file_name.startswith("_")]


@eel.expose
def get_language_support():
    java_return_code = os.system("java -version 2> nul")
    node_return_code = os.system("node --version> nul")
    # Only bother returning iffy languages. No point in sending 'python': True
    return {
        'java': java_return_code == 0,
        'node': node_return_code == 0,
        'chrome': is_chrome_installed(),  # Scratch bots need chrome to auto-run
        'fullpython': is_full_python(),
    }


@eel.expose
def get_match_options():
    return {
        'map_types': map_types + find_all_custom_maps(),
        'game_modes': game_mode_types,
        'match_behaviours': existing_match_behavior_types,
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
    exit_code = subprocess.call([sys.executable, "-m", "pip", "install", '--upgrade', '--no-warn-script-location', package_string])
    print(exit_code)
    return {'exitCode': exit_code, 'package': package_string}


@eel.expose
def install_requirements(config_path):
    try:
        bundle = get_bot_config_bundle(config_path)
    except Exception:
        bundle = get_script_config_bundle(config_path)

    if bundle.requirements_file:
        exit_code = install_requirements_file(bundle.requirements_file)
        return {'exitCode': exit_code, 'package': bundle.requirements_file}
    else:
        return {'exitCode': 1, 'package': None}


def get_last_botpack_commit_id():
    url = f'https://api.github.com/repos/{BOTPACK_REPO_OWNER}/{BOTPACK_REPO_NAME}/branches/{BOTPACK_REPO_BRANCH}'
    try:
        return get_json_from_url(url)['commit']['sha']
    except:
        return 'unknown'

@eel.expose
def get_downloaded_botpack_commit_id():
    settings = load_settings()
    local_commit_id = settings.value(COMMIT_ID_KEY, type=str)
    return local_commit_id


@eel.expose
def is_botpack_up_to_date():
    local_commit_id = get_downloaded_botpack_commit_id()

    if not local_commit_id:
        return False

    github_commit_id = get_last_botpack_commit_id()

    if github_commit_id == 'unknown':
        return True

    return github_commit_id == local_commit_id


def get_content_folder():
    if Path(os.getcwd()).name == 'RLBotGUI':
        # This is the classic case where we're using embedded python, and our current working directory is already
        # something like C:\Users\tareh\AppData\Local\RLBotGUI. It will also match if you have cloned RLBotGUI.
        return Path(os.getcwd())

    # If we get here, we're likely using system python or something along those lines.
    local_app_data = os.getenv('LOCALAPPDATA')
    if local_app_data:
        # We appear to be on Windows platform. This is where the new Windows launch script puts things.
        guix_path = Path(os.getenv('LOCALAPPDATA')) / 'RLBotGUIX'
        guix_path.mkdir(exist_ok=True)
        return guix_path

    # Probably on linux or mac at this point. Go with CWD again, because that's what they've used historically.
    return Path(os.getcwd())


def update_gui_after_botpack_update(botpack_location, botpack_status, additional_settings=None):
    if botpack_status is BotpackStatus.SUCCESS:
        # Configure the folder settings.
        bot_folder_settings['folders'][str(botpack_location)] = {'visible': True}

        settings = load_settings()
        settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
        if additional_settings:
            for key, value in additional_settings.items():
                settings.setValue(key, value)
        settings.sync()
        scan_for_bots()


@eel.expose
def download_bot_pack():
    botpack_location = get_content_folder() / BOTPACK_FOLDER
    botpack_status = RepoDownloader().download(BOTPACK_REPO_OWNER, BOTPACK_REPO_NAME, botpack_location)

    additional_settings = {COMMIT_ID_KEY: get_last_botpack_commit_id()}
    update_gui_after_botpack_update(botpack_location, botpack_status, additional_settings)


@eel.expose
def update_map_pack():
    location = get_content_folder() / MAPPACK_FOLDER

    updater = MapPackUpdater(location, MAPPACK_REPO[0], MAPPACK_REPO[1])
    map_index_old = updater.get_map_index()
    status = updater.needs_update()

    if status == BotpackStatus.REQUIRES_FULL_DOWNLOAD:
        status = RepoDownloader().download(
            MAPPACK_REPO[0],
            MAPPACK_REPO[1],
            location,
            update_tag_setting=False)

        map_index = updater.get_map_index()

        if map_index is None:
            print("ERROR: Updating mappack failed! There is no revision")
            return
        updater.hydrate_map_pack(map_index_old)

    update_gui_after_botpack_update(location, status)


@eel.expose
def get_map_pack_revision():
    location = get_content_folder() / MAPPACK_FOLDER
    updater = MapPackUpdater(location, MAPPACK_REPO[0], MAPPACK_REPO[1])
    index = updater.get_map_index()
    return index["revision"] if index is not None and "revision" in index else None


@eel.expose
def update_bot_pack():
    botpack_location = get_content_folder() / BOTPACK_FOLDER
    botpack_status = BotpackUpdater().update(BOTPACK_REPO_OWNER, BOTPACK_REPO_NAME, botpack_location)

    if botpack_status == BotpackStatus.REQUIRES_FULL_DOWNLOAD:
        botpack_status = RepoDownloader().download(BOTPACK_REPO_OWNER, BOTPACK_REPO_NAME, botpack_location)

    additional_settings = {COMMIT_ID_KEY: get_last_botpack_commit_id()}
    update_gui_after_botpack_update(botpack_location, botpack_status, additional_settings)


@eel.expose
def get_recommendations():
    try:
        # Load recommendations.json
        botpack_folder = get_content_folder() / BOTPACK_FOLDER
        file = open(botpack_folder / f'{BOTPACK_REPO_NAME}-{BOTPACK_REPO_BRANCH}' / 'RLBotPack' / 'recommendations.json')
        data = json.load(file)

        # Replace bot names with bot bundles with matching names from the botpack
        bots_in_botpack = get_bots_from_directory(botpack_folder)
        for recommendation in data['recommendations']:
            bot_names = recommendation['bots']
            bots = [next(bot for bot in bots_in_botpack if bot['name'] == name) for name in bot_names]
            recommendation['bots'] = bots

        return data

    except:
        return None


@eel.expose
def show_path_in_explorer(path_str):
    import subprocess
    path = Path(path_str)
    directory = path if path.is_dir() else path.parent
    subprocess.Popen(f'explorer "{directory}"')


@eel.expose
def hot_reload_python_bots():
    hot_reload_bots()


def ensure_bot_directory():
    content_folder = get_content_folder()
    bot_directory = content_folder / CREATED_BOTS_FOLDER
    bot_directory.mkdir(exist_ok=True)

    bot_folder_settings['folders'][str(bot_directory)] = {'visible': True}
    settings = load_settings()
    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.sync()

    return bot_directory


@eel.expose
def begin_python_bot(bot_name):
    bot_directory = ensure_bot_directory()

    try:
        config_file = bootstrap_python_bot(bot_name, bot_directory)
        return {'bots': load_bot_bundle(config_file)}
    except FileExistsError as e:
        return {'error': str(e)}


@eel.expose
def begin_scratch_bot(bot_name):
    bot_directory = ensure_bot_directory()

    try:
        config_file = bootstrap_scratch_bot(bot_name, bot_directory)
        install_package('webdriver_manager')  # Scratch bots need this, and the GUI's python doesn't have it by default.
        return {'bots': load_bot_bundle(config_file)}
    except FileExistsError as e:
        return {'error': str(e)}


@eel.expose
def begin_python_hivemind(hive_name):
    bot_directory = ensure_bot_directory()

    try:
        config_file = bootstrap_python_hivemind(hive_name, bot_directory)
        return {'bots': load_bot_bundle(config_file)}
    except FileExistsError as e:
        return {'error': str(e)}


@eel.expose
def set_state(state):
    set_game_state(state)


@eel.expose
def fetch_game_tick_packet_json():
    """
    Here we're selectively converting parts of the game tick packet into dict format,
    which will automatically get serialized into json by eel. We're skipping over parts
    that are currently not needed by the GUI, e.g. boost pad state.
    """
    ctypes_packet = fetch_game_tick_packet()
    dict_version = convert_packet_to_dict(ctypes_packet)
    return dict_version  # This gets converted to json automatically.


should_quit = False


def on_websocket_close(page, sockets):
    global should_quit
    eel.sleep(3.0)  # We might have just refreshed. Give the websocket a moment to reconnect.
    if not len(eel._websockets):
        # At this point we think the browser window has been closed.
        should_quit = True
        shut_down()


def is_chrome_installed():
    # Lots of hasattr checks because we're currently stuck supporting multiple versions of eel at once.
    if hasattr(eel.browsers, 'chr'):
        return eel.browsers.chr.get_instance_path() is not None
    else:
        chm = eel.browsers.chm
        if hasattr(chm, 'get_instance_path'):
            return chm.get_instance_path() is not None

        return chm.find_path() is not None


def is_full_python():
    # As opposed to embedded python. A full python installation is better at package management,
    # has access to tkinter, etc. This logic might be brittle; it's based on the historical fact that
    # our embedded installer always put python within the RLBotGUI directory.
    if 'RLBotGUI' in Path(sys.executable).parts:
        return False
    return True


def launch_eel(use_chrome):
    port = 40993  # Arbitrary choice from the 'registered sockets' range of 1024 to 49151
    options = {'port': port}

    if use_chrome:
        # Don't put anything in the options dict. The dict is used by old eel,
        # and old eel (0.10) defaults nicely to chrome app.
        browser_mode = 'chrome'  # New eel (1.0) needs it to be 'chrome'.
    else:
        browser_mode = 'system-default'
        options['mode'] = browser_mode

    # This disable_cache thing only works if you have tare's fork of eel https://github.com/ChrisKnott/Eel/pull/102
    # installed to pip locally using this technique https://stackoverflow.com/a/49684835
    # The suppress_error=True avoids the error "'options' argument deprecated in v1.0.0", we need to keep the
    # options argument since a lot of our user base has an older version of eel.
    eel.start('main.html', size=(1300, 870), block=False, callback=on_websocket_close, options=options,
              disable_cache=True, mode=browser_mode, port=port, suppress_error=True)


def init_settings():
    settings = load_settings()
    global bot_folder_settings
    bot_folder_settings = settings.value(BOT_FOLDER_SETTINGS_KEY, type=dict)

    if not bot_folder_settings:
        bot_folder_settings = {'files': {}, 'folders': {}}
        default_folder = settings.value(DEFAULT_BOT_FOLDER, type=str)
        if default_folder:
            bot_folder_settings['folders'][default_folder] = {'visible': True}


def start():
    init_settings()
    gui_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gui')
    eel.init(gui_folder)

    try:
        if not is_chrome_installed():
            raise Exception("Chrome does not appear to be installed.")
        launch_eel(use_chrome=True)
    except Exception as e:
        print(f'Falling back to system default browser because: {str(e)}')
        launch_eel(use_chrome=False)

    while not should_quit:
        do_infinite_loop_content()
        eel.sleep(1.0)
