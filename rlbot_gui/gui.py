import os
import shutil

import eel
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QFileDialog
from pip._internal import main as pipmain
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
from rlbot.parsing.match_settings_config_parser import map_types, game_mode_types, \
    boost_amount_mutator_types, match_length_types, max_score_types, overtime_mutator_types, \
    series_length_mutator_types, game_speed_mutator_types, ball_max_speed_mutator_types, ball_type_mutator_types, \
    ball_weight_mutator_types, ball_size_mutator_types, ball_bounciness_mutator_types, rumble_mutator_types, \
    boost_strength_mutator_types, gravity_mutator_types, demolish_mutator_types, respawn_time_mutator_types, \
    existing_match_behavior_types

from rlbot_gui.bot_management.bot_creation import bootstrap_python_bot, bootstrap_scratch_bot, convert_to_filename
from rlbot_gui.bot_management.downloader import BotpackDownloader, get_json_from_url
from rlbot_gui.match_runner.match_runner import hot_reload_bots, shut_down, start_match_helper, do_infinite_loop_content

DEFAULT_BOT_FOLDER = 'default_bot_folder'
BOTPACK_FOLDER = 'RLBotPackDeletable'
OLD_BOTPACK_FOLDER = 'RLBotPack'
BOTPACK_REPO_OWNER = 'RLBot'
BOTPACK_REPO_NAME = 'RLBotPack'
BOTPACK_REPO_BRANCH = 'master'
CREATED_BOTS_FOLDER = 'MyBots'
BOT_FOLDER_SETTINGS_KEY = 'bot_folder_settings'
MATCH_SETTINGS_KEY = 'match_settings'
TEAM_SETTINGS_KEY = 'team_settings'
COMMIT_ID_KEY = 'latest_botpack_commit_id'
settings = QSettings('rlbotgui', 'preferences')

bot_folder_settings = settings.value(BOT_FOLDER_SETTINGS_KEY, type=dict)

if not bot_folder_settings:
    bot_folder_settings = {'files': {}, 'folders': {}}
    default_folder = settings.value(DEFAULT_BOT_FOLDER, type=str)
    if default_folder:
        bot_folder_settings['folders'][default_folder] = {'visible': True}


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
        bot_folder_settings['folders'][filename] = {'visible': True}
        settings.setValue(DEFAULT_BOT_FOLDER, filename)
        settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
        settings.sync()
        return scan_for_bots()

    return []


def serialize_bundle(bundle):
    return {
        'name': bundle.name,
        'type': 'rlbot',
        'skill': 1,
        'image': 'imgs/rlbot.png',
        'path': bundle.config_path,
        'info': read_info(bundle),
        'logo': try_copy_logo(bundle)
    }


def load_bundle(filename):
    try:
        bundle = get_bot_config_bundle(filename)
        return [serialize_bundle(bundle)]
    except Exception as e:
        print(e)

    return []


@eel.expose
def pick_bot_config():
    filename = pick_bot_location(False)
    bot_folder_settings['files'][filename] = {'visible': True}
    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.sync()
    return load_bundle(filename)


@eel.expose
def get_folder_settings():
    return bot_folder_settings


@eel.expose
def save_folder_settings(folder_settings):
    global bot_folder_settings
    bot_folder_settings = folder_settings
    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.sync()


def validate_bots(bots):
    '''Reload rlbot controlled bot bundles and remove invalid ones'''
    valid_bots = []

    for bot in bots:
        if bot["type"] in ('rlbot', 'party_member_bot'):
            valid_bots += load_bundle(bot["path"])
        else:
            valid_bots.append(bot)

    return valid_bots


@eel.expose
def get_match_settings():
    match_settings = settings.value(MATCH_SETTINGS_KEY, type=dict)
    return match_settings if match_settings else None


@eel.expose
def get_team_settings():
    team_settings = settings.value(TEAM_SETTINGS_KEY, type=dict)
    if not team_settings:
        return None

    return {
        "blue_team": validate_bots(team_settings["blue_team"]),
        "orange_team": validate_bots(team_settings["orange_team"])
    }


@eel.expose
def save_match_settings(match_settings):
    settings.setValue(MATCH_SETTINGS_KEY, match_settings)


@eel.expose
def save_team_settings(blue_bots, orange_bots):
    settings.setValue(TEAM_SETTINGS_KEY, {"blue_team" : blue_bots, "orange_team": orange_bots})


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
def scan_for_bots():
    bot_hash = {}

    for folder, props in bot_folder_settings['folders'].items():
        if props['visible']:
            bots = get_bots_from_directory(folder)
            for bot in bots:
                bot_hash[bot['path']] = bot

    for file, props in bot_folder_settings['files'].items():
        if props['visible']:
            bots = load_bundle(file)  # Returns a list of size 1
            for bot in bots:
                bot_hash[bot['path']] = bot

    return list(bot_hash.values())


def try_copy_logo(bundle: BotConfigBundle):
    logo_path = bundle.get_logo_file()
    if logo_path is not None and os.path.exists(logo_path):
        web_url = 'imgs/logos/' + convert_to_filename(bundle.name) + '/' + convert_to_filename(logo_path)
        target_file = os.path.join(os.path.dirname(__file__), 'gui', web_url)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        shutil.copy(logo_path, target_file)
        return web_url
    return None


def get_bots_from_directory(bot_directory):
    return [serialize_bundle(bundle) for bundle in scan_directory_for_bot_configs(bot_directory)]


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
    exit_code = pipmain(['install', package_string])
    print(exit_code)
    return {'exitCode': exit_code, 'package': package_string}


def get_last_botpack_commit_id():
    url = f'https://api.github.com/repos/{BOTPACK_REPO_OWNER}/{BOTPACK_REPO_NAME}/branches/{BOTPACK_REPO_BRANCH}'
    try:
        return get_json_from_url(url)['commit']['sha']
    except:
        return 'unknown'


@eel.expose
def is_botpack_up_to_date():
    local_commit_id = settings.value(COMMIT_ID_KEY, type=str)

    if not local_commit_id:
        return False

    github_commit_id = get_last_botpack_commit_id()

    if github_commit_id == 'unknown':
        return True

    return github_commit_id == local_commit_id


@eel.expose
def download_bot_pack():
    # The bot pack in now hosted at https://github.com/RLBot/RLBotPack
    BotpackDownloader().download(BOTPACK_REPO_OWNER, BOTPACK_REPO_NAME, BOTPACK_REPO_BRANCH, BOTPACK_FOLDER)

    # Configure the folder settings.
    bot_folder_settings['folders'][os.path.abspath(BOTPACK_FOLDER)] = {'visible': True}

    if os.path.abspath(OLD_BOTPACK_FOLDER) in bot_folder_settings['folders']:
        # Toggle off the old one since it's been replaced.
        bot_folder_settings['folders'][os.path.abspath(OLD_BOTPACK_FOLDER)] = {'visible': False}

    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.setValue(COMMIT_ID_KEY, get_last_botpack_commit_id())
    settings.sync()


@eel.expose
def show_bot_in_explorer(bot_cfg_path):
    import subprocess
    directory = os.path.dirname(bot_cfg_path)
    subprocess.Popen(f'explorer "{directory}"')


@eel.expose
def hot_reload_python_bots():
    hot_reload_bots()


def ensure_bot_directory():
    bot_directory = CREATED_BOTS_FOLDER
    if not os.path.exists(bot_directory):
        os.mkdir(bot_directory)

    bot_folder_settings['folders'][os.path.abspath(CREATED_BOTS_FOLDER)] = {'visible': True}
    settings.setValue(BOT_FOLDER_SETTINGS_KEY, bot_folder_settings)
    settings.sync()

    return bot_directory


@eel.expose
def begin_python_bot(bot_name):
    bot_directory = ensure_bot_directory()

    try:
        config_file = bootstrap_python_bot(bot_name, bot_directory)
        return {'bots': load_bundle(config_file)}
    except FileExistsError as e:
        return {'error': str(e)}


@eel.expose
def begin_scratch_bot(bot_name):
    bot_directory = ensure_bot_directory()

    try:
        config_file = bootstrap_scratch_bot(bot_name, bot_directory)
        install_package('webdriver_manager')  # Scratch bots need this, and the GUI's python doesn't have it by default.
        return {'bots': load_bundle(config_file)}
    except FileExistsError as e:
        return {'error': str(e)}


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


def launch_eel(use_chrome):
    port = 51993
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
    eel.start('main.html', size=(1000, 830), block=False, callback=on_websocket_close, options=options,
              disable_cache=True, mode=browser_mode, port=port, suppress_error=True)


def start():
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
