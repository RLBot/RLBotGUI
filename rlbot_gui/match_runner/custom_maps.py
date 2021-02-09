"""
Helpers to load and set up matches in custom maps
"""

from contextlib import contextmanager
from datetime import datetime
from os import path

from typing import List, Optional

import glob
import shutil
import os

from rlbot.setup_manager import (
    SetupManager,
    RocketLeagueLauncherPreference,
    try_get_steam_executable_path,
)
from rlbot.gamelaunch.epic_launch import locate_epic_games_launcher_rocket_league_binary
from rlbot.utils import logging_utils

from rlbot_gui.persistence.settings import load_settings, BOT_FOLDER_SETTINGS_KEY

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

    # check if there metadata for the custom file
    expected_config_name = "_" + path.basename(custom_map_file)[:-4] + ".cfg"
    config_path = path.join(path.dirname(custom_map_file), expected_config_name)
    additional_info = {
        "original_path": custom_map_file,
    }
    if path.exists(config_path):
        additional_info["config_path"] = config_path


    real_map_file = path.join(rl_directory, CUSTOM_MAP_TARGET["filename"])
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    temp_filename = real_map_file + "." + timestamp

    shutil.copy2(real_map_file, temp_filename)
    logger.info("Copied real map to %s", temp_filename)
    shutil.copy2(custom_map_file, real_map_file)
    logger.info("Copied custom map from %s", custom_map_file)

    try:
        yield CUSTOM_MAP_TARGET["game_map"], additional_info
    finally:
        os.replace(temp_filename, real_map_file)
        logger.info("Reverted real map to %s", real_map_file)


def convert_custom_map_to_path(custom_map: str) -> Optional[str]:
    """
    Search through user's selected folders to find custom_map
    Return none if not found, full path if found
    """
    custom_map_file = None
    folders = get_search_folders()
    for folder in folders:
        scan_query = path.join(glob.escape(folder), "**", custom_map)
        for match in glob.iglob(scan_query, recursive=True):
            custom_map_file = match

    if not custom_map_file:
        logger.warning("%s - map doesn't exist", custom_map)

    return custom_map_file


def find_all_custom_maps() -> List[str]:
    """
    Ignores maps starting with _
    """
    folders = get_search_folders()
    maps = []
    for folder in folders:
        scan_query = path.join(glob.escape(folder), "**", "*.u[pd]k")
        for match in glob.iglob(scan_query, recursive=True):
            basename = path.basename(match)
            if basename.startswith("_"):
                continue
            maps.append(basename)
    return maps


def get_search_folders() -> List[str]:
    """Get all folders to search for maps"""
    bot_folders_setting = load_settings().value(BOT_FOLDER_SETTINGS_KEY, type=dict)
    folders = {}
    if "folders" in bot_folders_setting:
        folders = bot_folders_setting["folders"]
    return [k for k, v in folders.items() if v['visible']]


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
