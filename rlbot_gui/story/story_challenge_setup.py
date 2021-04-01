from datetime import datetime
from os import path
from typing import List, Tuple

import json
import random
import time
import traceback

import eel
from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.parsing.bot_config_bundle import get_bot_config_bundle
from rlbot.parsing.agent_config_parser import load_bot_appearance
from rlbot.utils.game_state_util import GameState, CarState
from rlbot.utils.structures.game_data_struct import GameTickPacket, Vector3
from rlbot.parsing.match_settings_config_parser import (
    game_mode_types,
    boost_amount_mutator_types,
    map_types,
    max_score_types,
    rumble_mutator_types,
    match_length_types,
)
from rlbot.matchconfig.match_config import (
    PlayerConfig,
    MatchConfig,
    MutatorConfig,
    Team,
    ScriptConfig,
)
from rlbot.setup_manager import SetupManager, RocketLeagueLauncherPreference

from rlbot_gui.match_runner.match_runner import get_fresh_setup_manager, setup_match


from rlbot_gui import gui as rlbot_gui  # TODO: Need to remove circular import

WITNESS_ID = random.randint(0, 1e5)
RENDERING_GROUP = "STORY"

DEBUG_MODE_SHORT_GAMES = False

def setup_failure_freeplay(setup_manager: SetupManager, message: str, color_key="red"):
    setup_manager.shut_down()
    match_config = MatchConfig()
    match_config.game_mode = game_mode_types[0]
    match_config.game_map = "BeckwithPark"
    match_config.enable_rendering = True

    mutators = MutatorConfig()
    mutators.match_length = match_length_types[3]
    match_config.mutators = mutators

    match_config.player_configs = []

    setup_manager.load_match_config(match_config)
    setup_manager.start_match()

    # wait till num players is 0
    wait_till_cars_spawned(setup_manager, 0)

    color = getattr(setup_manager.game_interface.renderer, color_key)()
    setup_manager.game_interface.renderer.begin_rendering(RENDERING_GROUP)
    # setup_manager.game_interface.renderer.draw_rect_2d(20, 20, 800, 800, True, setup_manager.game_interface.renderer.black())
    setup_manager.game_interface.renderer.draw_string_2d(20, 200, 4, 4, message, color)
    setup_manager.game_interface.renderer.end_rendering()


def make_match_config(
    challenge: dict, upgrades: dict, player_configs: List[PlayerConfig], script_configs: List[ScriptConfig]
):
    """Setup the match, following the challenge rules and user's upgrades
    """
    match_config = MatchConfig()

    match_config.game_mode = game_mode_types[0]  # Soccar
    if challenge.get("limitations", []).count("half-field"):
        match_config.game_mode = game_mode_types[5] # Heatseeker
    match_config.game_map = challenge.get("map")
    match_config.enable_state_setting = True

    match_config.mutators = MutatorConfig()
    match_config.mutators.max_score = challenge.get("max_score")
    if DEBUG_MODE_SHORT_GAMES:
        match_config.mutators.max_score = "3 Goals"

    if challenge.get("disabledBoost"):
        match_config.mutators.boost_amount = boost_amount_mutator_types[4]  # No boost

    if "rumble" in upgrades:
        match_config.mutators.rumble = rumble_mutator_types[1]  # All rumble

    match_config.player_configs = player_configs
    match_config.script_configs = script_configs
    return match_config


def collapse_path(cfg_path):
    if isinstance(cfg_path, list):
        cfg_path = path.join(*cfg_path)

    if "$RLBOTPACKROOT" in cfg_path:
        for bot_folder in rlbot_gui.bot_folder_settings["folders"].keys():
            adjusted_folder = path.join(bot_folder, "RLBotPack-master")
            subbed_path = cfg_path.replace("$RLBOTPACKROOT", adjusted_folder)
            if path.exists(subbed_path):
                cfg_path = subbed_path
                break

    return cfg_path


def rlbot_to_player_config(player: dict, team: Team):
    bot_path = collapse_path(player["path"])

    player_config = PlayerConfig()
    player_config.bot = True
    player_config.rlbot_controlled = True
    player_config.name = player["name"]
    player_config.team = team.value
    player_config.config_path = bot_path
    config = get_bot_config_bundle(bot_path)
    loadout = load_bot_appearance(config.get_looks_config(), team.value)
    player_config.loadout_config = loadout
    return player_config


def script_path_to_script_config(script_path):
    script_path = collapse_path(script_path)
    return ScriptConfig(script_path)


def make_human_config(team: Team):
    player_config = PlayerConfig()
    player_config.bot = False
    player_config.rlbot_controlled = False
    player_config.human_index = 0
    player_config.team = team.value
    player_config.name = ""

    return player_config


def pysonix_to_player_config(player: dict, team: Team):
    player_config = PlayerConfig()
    player_config.bot = True
    player_config.rlbot_controlled = False
    player_config.bot_skill = player["skill"] if "skill" in player else 1
    player_config.name = player["name"]
    player_config.team = team.value
    # should be able to customize "loadout_config"

    return player_config


def bot_to_player(player: dict, team: Team):
    """Helper to choose the right config for a bot"""
    if player["type"] == "psyonix":
        return pysonix_to_player_config(player, team)
    else:
        return rlbot_to_player_config(player, team)


def make_player_configs(
    challenge: dict, human_picks: List[int], team_info: dict, teammates: List[dict], all_bots
):
    player_configs = []
    player_configs.append(make_human_config(Team.BLUE))

    for i in range(challenge["humanTeamSize"] - 1):
        print(i)
        teammate = all_bots[human_picks[i]]
        config = bot_to_player(teammate, Team.BLUE)
        config.loadout_config.custom_color_id = team_info["color_secondary"]
        player_configs.append(config)

    for opponent in challenge["opponentBots"]:
        bot = bot_to_player(all_bots[opponent], Team.ORANGE)
        color = challenge.get("city_description", {}).get("color")
        if color:
            bot.loadout_config.team_color_id = color
        player_configs.append(bot)

    return player_configs


def make_script_configs(
    challenge: dict, all_scripts
):
    script_configs = []

    for script in challenge.get("scripts", []):
        script_config = script_path_to_script_config(all_scripts[script]["path"])
        script_configs.append(script_config)

    return script_configs


def packet_to_game_results(game_tick_packet: GameTickPacket):
    """Take the final game_tick_packet and
    returns the info related to the final game results
    """
    players = game_tick_packet.game_cars
    human_player = next(p for p in players if not p.is_bot)

    player_stats = [
        {
            "name": p.name,
            "team": p.team,
            # these are always 0, so we don't add them
            # "spawn_id": p.spawn_id,
            # "score": p.score_info.score,
            # "goals": p.score_info.goals,
            # "own_goals": p.score_info.own_goals,
            # "assists": p.score_info.assists,
            # "saves": p.score_info.saves,
            # "shots": p.score_info.shots,
            # "demolitions": p.score_info.demolitions
        }
        for p in players
        if p.name
    ]

    scores_sorted = [
        {"team_index": t.team_index, "score": t.score} for t in game_tick_packet.teams
    ]
    scores_sorted.sort(key=lambda x: x["score"], reverse=True)
    human_won = scores_sorted[0]["team_index"] == human_player.team

    return {
        "human_team": human_player.team,
        "score": scores_sorted,  # [{team_index, score}]
        "stats": player_stats,
        "human_won": human_won,
        "timestamp": datetime.now().isoformat(),
    }


def has_user_perma_failed(challenge, manual_stats):
    """
    Check if the user has perma-failed the challenge
    meaning more time in the game doesn't change the result
    """
    if "completionConditions" not in challenge:
        return False
    failed = False
    completionConditions = challenge["completionConditions"]

    if "selfDemoCount" in completionConditions:
        survived = (
            manual_stats["recievedDemos"] <= completionConditions["selfDemoCount"]
        )
        failed = failed or not survived
    return failed

def end_by_mercy(challenge, manual_stats, results):
    """Returns true if the human team is ahead by a lot
    and the other challenges have finished"""
    challenge_completed = calculate_completion(challenge, manual_stats, results)

    mercy_difference = 5
    # ignore the team, just look at the differential
    score_differential = results["score"][0]["score"] - results["score"][1]["score"]

    return score_differential >= mercy_difference and challenge_completed


def calculate_completion(challenge, manual_stats, results):
    """
    parse challenge to file completionConditions and evaluate
    each.
    All conditions are "and"
    """
    completed = results["human_won"]
    if "completionConditions" not in challenge:
        return completed

    if has_user_perma_failed(challenge, manual_stats):
        return False

    completionConditions = challenge["completionConditions"]

    if not completionConditions.get("win", True):
        # the "win" requirement is explicitly off
        completed = True

    if "scoreDifference" in completionConditions:
        # ignore the team, jsut look at the differential
        condition = completionConditions["scoreDifference"]
        difference = results["score"][0]["score"] - results["score"][1]["score"]
        completed = completed and (difference >= condition)

    if "demoAchievedCount" in completionConditions:
        achieved = (
            manual_stats["opponentRecievedDemos"]
            >= completionConditions["demoAchievedCount"]
        )
        completed = completed and achieved

    if "goalsScored" in completionConditions:
        achieved = manual_stats["humanGoalsScored"] >= completionConditions["goalsScored"]
        completed = completed and achieved

    return completed


class ManualStatsTracker:
    def __init__(self, challenge):
        self.stats = {
            "recievedDemos": 0,  # how many times the human got demo'd
            "opponentRecievedDemos": 0,  # how many times the opponents were demo'd
            "humanGoalsScored": 0,
        }

        self._challenge = challenge
        self._player_count = challenge["humanTeamSize"] + len(challenge["opponentBots"])
        self._human_team = Team.BLUE.value  # hardcoded for now
        self._human_player_index = 0

        # helper to find discrete demo events
        self._in_demo_state = [False] * self._player_count
        # helper to find who scored!
        self._last_touch_by_team = [None, None]
        self._last_score_by_team = [0, 0]

    def updateStats(self, gamePacket: GameTickPacket):
        """
        Update and track stats based on the game packet
        """
        # keep track of demos
        for i in range(len(self._in_demo_state)):
            cur_player = gamePacket.game_cars[i]
            if self._in_demo_state[i]:  # we will toggle this if we have respawned
                self._in_demo_state[i] = cur_player.is_demolished
            elif cur_player.is_demolished:
                print("SOMEONE GOT DEMO'd")
                self._in_demo_state[i] = True
                if i == self._human_player_index:
                    self.stats["recievedDemos"] += 1
                elif i >= self._challenge["humanTeamSize"]:
                    # its an opponent bot
                    self.stats["opponentRecievedDemos"] += 1

        touch = gamePacket.game_ball.latest_touch
        team = touch.team
        self._last_touch_by_team[team] = touch

        for i in range(2):  # iterate of [{team_index, score}]
            team_index = gamePacket.teams[i].team_index
            new_score = gamePacket.teams[i].score
            if new_score != self._last_score_by_team[team_index]:
                self._last_score_by_team[team_index] = new_score

                if team_index == self._human_team and self._last_touch_by_team[team_index] is not None:
                    last_touch_player = self._last_touch_by_team[
                        team_index
                    ].player_index
                    last_touch_player_name = self._last_touch_by_team[
                        team_index
                    ].player_name
                    if last_touch_player == self._human_player_index and last_touch_player_name != "":
                        self.stats["humanGoalsScored"] += 1
                        print("humanGoalsScored")


def wait_till_cars_spawned(
    setup_manager: SetupManager, expected_player_count: int
) -> GameTickPacket:
    packet = GameTickPacket()
    setup_manager.game_interface.fresh_live_data_packet(packet, 1000, WITNESS_ID)
    waiting_start = time.monotonic()
    while packet.num_cars != expected_player_count and time.monotonic() - waiting_start < 5:
        print("Game started but no cars are in the packets")
        time.sleep(0.5)
        setup_manager.game_interface.fresh_live_data_packet(packet, 1000, WITNESS_ID)

    return packet


def manage_game_state(
    challenge: dict, upgrades: dict, setup_manager: SetupManager
) -> Tuple[bool, dict]:
    """
    Continuously track the game and adjust state to respect challenge rules and
    upgrades.
    At the end of the game, calculate results and the challenge completion
    and return that
    """
    early_failure = False, {}

    expected_player_count = challenge["humanTeamSize"] + len(challenge["opponentBots"])
    # Wait for everything to be initialized
    packet = wait_till_cars_spawned(setup_manager, expected_player_count)

    if packet.num_cars == 0:
        print("The game was initialized with no cars")
        return early_failure

    tick_rate = 120
    results = None
    max_boost = 0
    if "boost-100" in upgrades:
        max_boost = 100
    elif "boost-33" in upgrades:
        max_boost = 33

    half_field = challenge.get("limitations", []).count("half-field") > 0

    stats_tracker = ManualStatsTracker(challenge)
    last_boost_bump_time = time.monotonic()
    while True:
        try:
            eel.sleep(0)  # yield to allow other gui threads to operate.
            packet = GameTickPacket()
            setup_manager.game_interface.fresh_live_data_packet(
                packet, 1000, WITNESS_ID
            )

            if packet.num_cars == 0:
                # User seems to have ended the match
                print("User ended the match")
                return early_failure

            stats_tracker.updateStats(packet)
            results = packet_to_game_results(packet)

            if has_user_perma_failed(challenge, stats_tracker.stats):
                time.sleep(1)
                setup_failure_freeplay(setup_manager, "You failed the challenge!")
                return early_failure

            if end_by_mercy(challenge, stats_tracker.stats, results):
                time.sleep(3)
                setup_failure_freeplay(setup_manager, "Challenge completed by mercy rule!", "green")
                return True, results

            human_info = packet.game_cars[0]
            game_state = GameState()
            human_desired_state = CarState()
            game_state.cars = {0: human_desired_state}

            changed = False
            # adjust boost
            if human_info.boost > max_boost and not half_field:
                # Adjust boost, unless in heatseeker mode
                human_desired_state.boost_amount = max_boost
                changed = True

            if "boost-recharge" in upgrades:
                # increase boost at 10% per second
                now = time.monotonic()
                if human_info.boost < max_boost and (now - last_boost_bump_time > 0.1):
                    changed = True
                    last_boost_bump_time = now
                    human_desired_state.boost_amount = min(human_info.boost + 1, max_boost)


            if changed:
                setup_manager.game_interface.set_game_state(game_state)

            if packet.game_info.is_match_ended:
                break

        except KeyError:
            traceback.print_exc()
            # it means that the game was interrupted by the user
            print("Looks like the game is in a bad state")
            setup_failure_freeplay(setup_manager, "The game was interrupted.")
            return early_failure

    return calculate_completion(challenge, stats_tracker.stats, results), results




def run_challenge(
    match_config: MatchConfig, challenge: dict, upgrades: dict, launcher_pref: RocketLeagueLauncherPreference
) -> Tuple[bool, dict]:
    """Launch the game and keep track of the state"""
    setup_manager = get_fresh_setup_manager()
    setup_match(setup_manager, match_config, launcher_pref)

    setup_manager.game_interface.renderer.clear_screen(RENDERING_GROUP)
    game_results = None
    try:
        game_results = manage_game_state(challenge, upgrades, setup_manager)
    except:
        # no matter what happens we gotta continue
        traceback.print_exc()
        print("Something failed with the game. Will proceed with shutdown")
        # need to make failure apparent to user
        setup_failure_freeplay(setup_manager, "The game failed to continue")
        return False, {}

    setup_manager.shut_down()

    return game_results


def configure_challenge(challenge: dict, saveState, human_picks: List[int], all_bots, all_scripts):
    player_configs = make_player_configs(
        challenge, human_picks, saveState.team_info, saveState.teammates, all_bots
    )
    script_configs = make_script_configs(
        challenge, all_scripts
    )
    match_config = make_match_config(challenge, saveState.upgrades, player_configs, script_configs)

    return match_config