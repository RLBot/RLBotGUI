import tkinter
from tkinter import filedialog

import eel
from rlbot.parsing.agent_config_parser import get_bot_config_bundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

sm = None


def startMatchHelper(configuration):
    # TODO: use this configuration
    print(configuration)

    from rlbot.setup_manager import SetupManager
    global sm

    if sm is not None:
        sm.shut_down()

    sm = SetupManager()
    sm.connect_to_game()
    sm.load_config()
    sm.launch_ball_prediction()
    sm.launch_quick_chat_manager()
    sm.launch_bot_processes()
    sm.start_match()
    # Note that we are not calling infinite_loop because that is not compatible with the way eel works!
    # Instead we will reproduce the important behavior from infinite_loop inside this file.

@eel.expose
def startMatch(configuration):
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


def start():
    eel.init('gui')
    eel.start('main.html', size=(880, 660), block=False)

    while True:
        if sm:
            sm.try_recieve_agent_metadata()
        eel.sleep(1.0)
