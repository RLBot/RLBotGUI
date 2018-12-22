import eel

sm = None

@eel.expose
def startMatch():
    from rlbot.setup_manager import SetupManager
    sm = SetupManager()
    sm.startup()
    sm.load_config()
    sm.init_ball_prediction()
    sm.launch_bot_processes()
    sm.run()

@eel.expose
def killBots(self):
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")


eel.init('gui')
eel.start('main.html', size=(880, 660), block=True)