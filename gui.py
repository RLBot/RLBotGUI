import multiprocessing

import eel
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

sm = None


def startMatchHelper(configuration):
    from rlbot.setup_manager import SetupManager
    global sm
    sm = SetupManager()
    print('connecting to game')
    sm.connect_to_game()
    print('loading config')
    sm.load_config()
    print('launching ball prediction')
    sm.launch_ball_prediction()
    print('launching quick chat')
    # sm.launch_quick_chat_manager()
    print('launching bot processes')
    sm.launch_bot_processes()
    print('starting match')
    sm.start_match()
    print('starting infinite loop')
    sm.infinite_loop()


@eel.expose
def startMatch(configuration):
    print(configuration)  # TODO: use this configuration

    # TODO: figure out how to run the setup manager without blocking the eel process.
    # See the Asynchronous Python section here: https://github.com/ChrisKnott/Eel
    # process = multiprocessing.Process(target=startMatchHelper, args=(configuration))
    # process.start()
    eel.spawn(startMatchHelper(configuration))


@eel.expose
def killBots():
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")


@eel.expose
def scanForBots(directory):
    return [{'name': bundle.name, 'image': 'imgs/rlbot.png', 'path': bundle.config_path}
            for bundle in scan_directory_for_bot_configs(directory)]


eel.init('gui')
eel.start('main.html', size=(880, 660))
