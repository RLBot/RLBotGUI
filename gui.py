import tkinter
from tkinter import filedialog

import eel
from rlbot.parsing.agent_config_parser import get_bot_config_bundle
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
def pick_bot_folder():
    filename = pick_bot_location(True)

    if filename:
        return scanForBots(filename)

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

    # https://stackoverflow.com/a/7090747

    # Make a top-level instance and hide since it is ugly and big.
    root = tkinter.Tk()
    root.withdraw()

    # Make it almost invisible - no decorations, 0 size, top left corner.
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.attributes('-alpha', 0.3)
    root.attributes("-topmost", True)

    # Show window again and lift it to top so it can get focus,
    # otherwise dialogs will end up behind the terminal.
    root.deiconify()

    if is_folder:
        filename = filedialog.askdirectory(parent=root)  # Or some other dialog
    else:
        filename = filedialog.askopenfilename(parent=root)

    # Get rid of the top-level instance once to make it actually invisible.
    root.destroy()

    return filename

@eel.expose
def scanForBots(directory):
    return [{'name': bundle.name, 'image': 'imgs/rlbot.png', 'path': bundle.config_path}
            for bundle in scan_directory_for_bot_configs(directory)]


eel.init('gui')
eel.start('main.html', size=(880, 660))
