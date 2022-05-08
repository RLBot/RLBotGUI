from PyQt5.QtCore import QSettings
from rlbot.setup_manager import DEFAULT_LAUNCHER_PREFERENCE, RocketLeagueLauncherPreference

BOT_FOLDER_SETTINGS_KEY = 'bot_folder_settings'
MATCH_SETTINGS_KEY = 'match_settings'
LAUNCHER_SETTINGS_KEY = 'launcher_settings'
TEAM_SETTINGS_KEY = 'team_settings'


def load_settings() -> QSettings:
    return QSettings('rlbotgui', 'preferences')


def launcher_preferences_from_map(launcher_preference_map: dict) -> RocketLeagueLauncherPreference:
    exe_path_key = 'rocket_league_exe_path'
    exe_path = None
    if exe_path_key in launcher_preference_map:
        exe_path = launcher_preference_map[exe_path_key]
        if not exe_path:
            exe_path = None  # Don't pass in an empty string, pass None instead so it will be ignored.

    return RocketLeagueLauncherPreference(
        launcher_preference_map['preferred_launcher'],
        use_login_tricks=True,  # Epic launch now ONLY works with login tricks
        rocket_league_exe_path=exe_path,
    )


def load_launcher_settings():
    settings = load_settings()
    launcher_settings = settings.value(LAUNCHER_SETTINGS_KEY, type=dict)
    return launcher_settings if launcher_settings else DEFAULT_LAUNCHER_PREFERENCE.__dict__
