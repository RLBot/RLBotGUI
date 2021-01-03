"""
Helpers to load and set up matches in custom maps
"""

from contextlib import contextmanager
from datetime import datetime
from os import path

import shutil

from rlbot.setup_manager import (
    SetupManager,
    RocketLeagueLauncherPreference,
    try_get_steam_executable_path,
)
from rlbot.gamelaunch.epic_launch import locate_epic_games_launcher_rocket_league_binary
from rlbot.utils import logging_utils

CUSTOM_MAP_TARGET = {"filename": "Labs_Utopia_P.upk", "game_map": "UtopiaRetro"}

logger = logging_utils.get_logger("custom_maps")


@contextmanager
def prepare_custom_map(custom_map_file: str, rl_directory: str):
    """
    Provides a context manager. It will swap out the custom_map_file
    for an existing map in RL and it will return the `game_map`
    name that should be used in a MatchConfig.

    Once the context is left, the original map is replaced back.
    The context should be left as soon as the match has started
    """
    real_map_file = path.join(rl_directory, CUSTOM_MAP_TARGET["filename"])
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    temp_filename = real_map_file + "." + timestamp

    shutil.copy2(real_map_file, temp_filename)
    logger.info("Copied real map to %s", temp_filename)
    shutil.copy2(custom_map_file, real_map_file)
    logger.info("Copied custom map from %s", custom_map_file)

    try:
        yield CUSTOM_MAP_TARGET["game_map"]
    finally:
        shutil.move(temp_filename, real_map_file)
        logger.info("Reverted real map to %s", real_map_file)


def convert_custom_map_to_path(custom_map: str):
    custom_map_dir = get_custom_map_dir()
    custom_map_file = path.join(custom_map_dir, custom_map)
    if not path.exists(custom_map_file):
        logger.warning("%s - map doesn't exist", custom_map_file)
        return None

    return custom_map_file


def get_custom_map_dir():
    """Probably will get from storage or something?"""
    custom_map_dir = r"C:\Users\Triton\Downloads\Simplicity"  # temp hardcoding
    return custom_map_dir


def identify_map_directory(launcher_pref: RocketLeagueLauncherPreference):
    """Find RocketLeague map directory"""
    final_path = None
    if launcher_pref.preferred_launcher == RocketLeagueLauncherPreference.STEAM:
        steam = try_get_steam_executable_path()
        suffix = r"steamapps\common\rocketleague\TAGame\CookedPCConsole"
        if not steam:
            return None

        # TODO: Steam can install RL on a different disk. Need to
        # read libraryfolders.vdf to detect this situation
        # It's a human-readable but custom format so not trivial to parse

        final_path = path.join(path.dirname(steam), suffix)
    else:
        rl_executable = locate_epic_games_launcher_rocket_league_binary()
        suffix = r"TAGame\CookedPCConsole"
        if not rl_executable:
            return None

        # Binaries/Win64/ is what we want to strip off
        final_path = path.join(path.dirname(rl_executable), "..", "..", suffix)

    if not path.exists(final_path):
        logger.warning("%s - directory doesn't exist", final_path)
        return None
    return final_path
