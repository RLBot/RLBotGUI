import os
import string
import tempfile

from configobj import ConfigObj
from rlbot.agents.base_agent import BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, PYTHON_FILE_KEY, BOT_CONFIG_AGENT_HEADER
from rlbot.parsing.agent_config_parser import PARTICIPANT_CONFIGURATION_HEADER

from rlbot_gui.bot_management.downloader import download_and_extract_zip


def convert_to_filename(text):
    """
    Normalizes string, converts to lowercase, removes non-alphanumeric characters,
    and converts spaces to underscores.
    """
    import unicodedata
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in normalized if c in valid_chars)
    filename = filename.replace(' ', '_')  # Replace spaces with underscores
    return filename


def bootstrap_python_bot(bot_name, directory):
    bot_directory = directory or "."
    sanitized_name = convert_to_filename(bot_name)

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)

        # This is a particular commit where we can be confident of the file structure. Feel free to update later.
        known_good_git_hash = '20e18ed55a3b3be771e6e97819169b3e4a278aab'

        download_and_extract_zip(
            download_url=f"https://github.com/RLBot/RLBotPythonExample/archive/{known_good_git_hash}.zip",
            local_zip_path=f"{tmpdirname}/RLBotPythonExample.zip", local_folder_path=tmpdirname)

        try:
            os.rename(f"{tmpdirname}/RLBotPythonExample-{known_good_git_hash}", f"{bot_directory}/{sanitized_name}")
        except FileExistsError:
            return {'error': f'There is already a bot named {sanitized_name}, please choose a different name!'}

    # Choose appropriate file names based on the bot name
    code_dir = f"{bot_directory}/{sanitized_name}/{sanitized_name}"
    python_file = f"{code_dir}/{sanitized_name}.py"
    config_file = f"{code_dir}/{sanitized_name}.cfg"

    os.rename(f"{bot_directory}/{sanitized_name}/python_example/", code_dir)
    os.rename(f"{code_dir}/python_example.py", python_file)
    os.rename(f"{code_dir}/python_example.cfg", config_file)

    # Update the config file to point to the renamed files, and show the correct bot name.
    # Use the ConfigObj library here instead of our custom implementation because it's much better at round-tripping.
    bot_config = ConfigObj(config_file)
    bot_config[BOT_CONFIG_MODULE_HEADER][BOT_NAME_KEY] = bot_name
    bot_config[BOT_CONFIG_MODULE_HEADER][PYTHON_FILE_KEY] = f"{sanitized_name}.py"
    bot_config.write()

    relative_config_path = f"{sanitized_name}/{sanitized_name}.cfg"
    rlbot_config = ConfigObj(f"{bot_directory}/{sanitized_name}/rlbot.cfg")
    for i in range(0, 10):
        rlbot_config[PARTICIPANT_CONFIGURATION_HEADER][f"participant_config_{i}"] = relative_config_path
    rlbot_config.write()

    # This is intended to open the example python file in the default system editor for .py files.
    # Hopefully this will be VS Code or notepad++ or something. If it gets executed as a python script, no harm done.
    os.startfile(python_file)

    return config_file


def bootstrap_scratch_bot(bot_name, directory):
    bot_directory = directory or "."
    sanitized_name = convert_to_filename(bot_name)

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)

        known_good_git_hash = '347b2616a66a3d20af0d59c6a1f89d61caa964fe'

        download_and_extract_zip(
            download_url=f"https://github.com/RLBot/RLBotScratchInterface/archive/{known_good_git_hash}.zip",
            local_zip_path=f"{tmpdirname}/RLBotScratchInterface.zip", local_folder_path=tmpdirname)

        try:
            os.rename(f"{tmpdirname}/RLBotScratchInterface-{known_good_git_hash}", f"{bot_directory}/{sanitized_name}")
        except FileExistsError:
            return {'error': f'There is already a bot named {sanitized_name}, please choose a different name!'}

    # Choose appropriate file names based on the bot name
    code_dir = f"{bot_directory}/{sanitized_name}/{sanitized_name}"
    scratch_file = f"{code_dir}/{sanitized_name}.sb3"
    config_file = f"{code_dir}/{sanitized_name}.cfg"

    os.rename(f"{bot_directory}/{sanitized_name}/scratch_bot/", code_dir)
    os.rename(f"{code_dir}/my_scratch_bot.sb3", scratch_file)
    os.rename(f"{code_dir}/my_scratch_bot.cfg", config_file)

    # Update the config file to point to the renamed files, and show the correct bot name.
    # Use the ConfigObj library here instead of our custom implementation because it's much better at round-tripping.
    bot_config = ConfigObj(config_file)
    bot_config[BOT_CONFIG_MODULE_HEADER][BOT_NAME_KEY] = bot_name
    bot_config[BOT_CONFIG_AGENT_HEADER]['sb3file'] = f"{sanitized_name}.sb3"
    bot_config.write()

    relative_config_path = f"{sanitized_name}/{sanitized_name}.cfg"
    rlbot_config = ConfigObj(f"{bot_directory}/{sanitized_name}/rlbot.cfg")
    for i in range(0, 10):
        rlbot_config[PARTICIPANT_CONFIGURATION_HEADER][f"participant_config_{i}"] = relative_config_path
    rlbot_config.write()

    return config_file
