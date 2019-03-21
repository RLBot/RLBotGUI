import random
import time
import traceback
from pathlib import Path
from contextlib import contextmanager

from rlbot.matchconfig.match_config import PlayerConfig, MatchConfig, MutatorConfig, Team
from rlbot.setup_manager import SetupManager
from rlbot.utils.logging_utils import get_logger
from rlbottraining.exercise_runner import load_default_playlist, run_playlist
from rlbottraining.history.exercise_result import log_result

from rlbot_gui.rlbottrainingpack.exercises import JSONExercise
from rlbot_gui.rlbottrainingpack.importer import import_pack

sm: SetupManager = None
in_training = False
logger = get_logger('training')


def create_player_config(bot, human_index_tracker: IncrementingInteger):
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


@contextmanager
def in_training_lock():
    global in_training
    if in_training:  # TODO: use an actual lock because of worries about async.
        return
    in_training = True
    try:
        yield
    except Exception:
        print("An error occurred trying to run training exercise:")
        traceback.print_exc()
    in_training = False

def start_training_helper(training_module: Path, customized_match_config: MatchConfig):
    with in_training_lock():
        playlist = load_default_playlist(training_module)()

        # Override attributes of the playlist with what the user
        # TODO: Deal with edits for the individual exercises as different exercises may have different numbers of bots in the same playlist
        for exercise in playlist:
            if customized_match_config.player_configs:
                exercise.match_config.player_configs = customized_match_config.player_configs
            # TODO: Copy mutators to/from the GUI.

        for result in run_playlist(playlist, seed=random.randint(1, 1000)):
            log_result(result, logger)


def start_match_helper(match_config: MatchConfig):

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


def do_infinite_loop_content():
    if sm is not None:
        sm.try_recieve_agent_metadata()


def hot_reload_bots():
    if sm is not None:
        sm.reload_all_agents()


def shut_down():
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")

