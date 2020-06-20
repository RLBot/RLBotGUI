import json
from os import path
import random

from datetime import datetime
import time
from typing import List, Tuple

from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.parsing.match_settings_config_parser import (
    game_mode_types,
    boost_amount_mutator_types,
    map_types,
    max_score_types,
    rumble_mutator_types,
)
from rlbot.matchconfig.match_config import (
    PlayerConfig,
    MatchConfig,
    MutatorConfig,
    Team,
)
from rlbot.setup_manager import SetupManager

from rlbot_gui.story.load_story_descriptions import BOTS_CONFIG

WITNESS_ID = random.randint(0, 1e5)

DEBUG_MODE_SHORT_GAMES = True


def make_match_config(
    challenge: dict, upgrades: dict, player_configs: List[PlayerConfig]
):
    """Setup the match, following the challenge rules and user's upgrades
    """
    match_config = MatchConfig()

    match_config.game_mode = game_mode_types[0]  # Soccar
    match_config.game_map = challenge.get("map")
    match_config.enable_state_setting = True

    match_config.mutators = MutatorConfig()
    match_config.mutators.max_score = challenge.get("max_score")
    if DEBUG_MODE_SHORT_GAMES:
        match_config.mutators.max_score = "3 Goals"

    if challenge.get("disabledBoost"):
        match_config.mutators.boost_amount = boost_amount_mutator_types[4]  # No boost

    if "rumble" in upgrades:
        match_config.mutators.rumble = rumble_mutator_types[3]  # Civilized

    match_config.player_configs = player_configs
    return match_config


def rlbot_to_player_config(player: dict, team: Team):
    player_config = PlayerConfig()
    player_config.bot = True
    player_config.rlbot_controlled = True
    player_config.name = player["name"]
    player_config.team = team.value
    player_config.config_path = player["path"]
    return player_config


def make_human_config(team: Team):
    player_config = PlayerConfig()
    player_config.bot = False
    player_config.rlbot_controlled = False
    player_config.human_index = 0
    player_config.team = team.value
    player_config.name = "WillThisMattet?"

    # i wonder if we can overwrite loadout_config
    return player_config


def pysonix_to_player_config(player: dict, team: Team):
    player_config = PlayerConfig()
    player_config.bot = True
    player_config.rlbot_controlled = False
    player_config.bot_skill = player["skill"]
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
    challenge: dict, human_picks: List[int], team_info: dict, teammates: List[dict]
):
    player_configs = []
    player_configs.append(make_human_config(Team.BLUE))

    for i in range(challenge["humanTeamSize"] - 1):
        print(i)
        teammate = BOTS_CONFIG[human_picks[i]]
        config = bot_to_player(teammate, Team.BLUE)
        player_configs.append(config)

    for opponent in challenge["opponentBots"]:
        bot = bot_to_player(BOTS_CONFIG[opponent], Team.ORANGE)
        player_configs.append(bot)

    return player_configs


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


def manage_game_state(
    challenge: dict, upgrades: dict, setup_manager: SetupManager
) -> Tuple[bool, dict]:
    """
    Continuously track the game and adjust state to respect challenge rules and
    upgrades.
    At the end of the game, calculate results and the challenge completion
    and return that
    """
    tick_rate = 120
    # completion_conditions = challenge["completionConditions"]
    results = None
    max_boost = 0
    if "boost-100" in upgrades:
        max_boost = 100
    elif "boost-33" in upgrades:
        max_boost = 33

    while True:
        try:
            game_tick_packet = GameTickPacket()
            packet = setup_manager.game_interface.fresh_live_data_packet(
                game_tick_packet, 1000, WITNESS_ID
            )

            # keep track of demo
            # adjust boost
            game_state = GameState.create_from_gametickpacket(packet)
            changed = False

            car = game_state.cars[0]
            if car.boost_amount > max_boost:
                car.boost_amount = max_boost
                changed = True

            if changed:
                setup_manager.game_interface.set_game_state(game_state)

            # only handle the win condition for now
            if packet.game_info.is_match_ended:
                results = packet_to_game_results(packet)
                break

            time.sleep(1.0 / tick_rate)
        except KeyError:
            # it means that the game was interrupted by the user
            print("Looks like the game is in a bad state")
            return False, {}

    # calculate completion
    completed = results["human_won"]
    if "completionConditions" in challenge:
        completionConditions = challenge["completionConditions"]

        if not completionConditions.get("win", True):
            # the "win" requirement is explicitly off
            completed = True

        if "scoreDifference" in completionConditions:
            print("In score diffie")
            # ignore the team, jsut look at the differential
            condition = completionConditions["scoreDifference"]
            difference = results["score"][0]["score"] - results["score"][1]["score"]
            print(f"{difference} >= {condition}")
            completed = completed and (difference >= condition)

    return completed, results


def run_challenge(
    match_config: MatchConfig, challenge: dict, upgrades: dict
) -> Tuple[bool, dict]:
    """Launch the game and keep track of the state"""
    setup_manager = SetupManager()
    setup_manager.early_start_seconds = 5
    setup_manager.connect_to_game()
    setup_manager.load_match_config(match_config)
    setup_manager.launch_early_start_bot_processes()
    setup_manager.start_match()
    setup_manager.launch_bot_processes()

    game_results = None
    try:
        game_results = manage_game_state(challenge, upgrades, setup_manager)
    except:
        # no matter what happens we gotta continue
        traceback.print_exc()
        print("Something failed with the game. Will proceed with shutdown")
    setup_manager.shut_down()

    if not game_results:
        return False, {}

    return game_results


def configure_challenge(challenge: dict, saveState, human_picks: List[int]):
    player_configs = make_player_configs(
        challenge, human_picks, saveState.team_info, saveState.teammates
    )
    match_config = make_match_config(challenge, saveState.upgrades, player_configs)

    return match_config
