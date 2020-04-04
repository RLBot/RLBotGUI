# https://stackoverflow.com/a/51704613
try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

DEFAULT_LOGGER = 'rlbot'


def upgrade():
    package = 'rlbot'

    import importlib
    import os
    folder = os.path.dirname(os.path.realpath(__file__))

    try:
        # https://stackoverflow.com/a/24773951
        importlib.import_module(package)

        from rlbot.utils import public_utils, logging_utils

        logger = logging_utils.get_logger(DEFAULT_LOGGER)
        if not public_utils.have_internet():
            logger.log(logging_utils.logging_level,
                       'Skipping upgrade check for now since it looks like you have no internet')
        elif public_utils.is_safe_to_upgrade():
            # Upgrade only the rlbot-related stuff.
            rlbot_requirements = os.path.join(folder, 'rlbot-requirements.txt')
            pipmain(['install', '-r', rlbot_requirements, '--upgrade'])

    except (ImportError, ModuleNotFoundError):
        # First time installation, install lots of stuff
        all_requirements = os.path.join(folder, 'requirements.txt')
        pipmain(['install', '-r', all_requirements])


if __name__ == '__main__':
    upgrade()
