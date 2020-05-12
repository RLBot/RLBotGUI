import shutil
from pathlib import Path

import os


def replace_upgrade_file():
    """
    RLBotGUI installations on windows generally have a file at ./pynsist_helpers/upgrade.py which is
    NOT part of the rlbot_gui python package. It lives outside the package for the sake of upgrading
    the package. However, sometimes we wish to push updates to upgrade.py without requiring users to
    manually reinstall. This function takes a version of the upgrade script vended inside rlbot_gui
    and copies it to the external location.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fresh_upgrade_file = Path(os.path.join(dir_path, 'upgrade_script.py'))
    existing_upgrade_file = Path('./pynsist_helpers/upgrade.py')

    if existing_upgrade_file.exists():
        shutil.copyfile(fresh_upgrade_file, existing_upgrade_file)
        print(f"Successfully replaced {existing_upgrade_file.absolute()}.")
