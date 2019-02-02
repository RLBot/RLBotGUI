import configparser
import os
import string
import tempfile

from rlbot.agents.base_agent import BaseAgent, BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, PYTHON_FILE_KEY

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

        download_and_extract_zip(
            download_url="https://github.com/RLBot/RLBotPythonExample/archive/master.zip",
            local_zip_path=f"{tmpdirname}/RLBotPythonExample.zip", local_folder_path=tmpdirname)

        try:
            os.rename(f"{tmpdirname}/RLBotPythonExample-master", f"{bot_directory}/{sanitized_name}")
        except FileExistsError:
            return {'error': f'There is already a bot named {sanitized_name}, please choose a different name!'}

    # Choose appropriate file names based on the bot name
    code_dir = f"{bot_directory}/{sanitized_name}/{sanitized_name}"
    python_file = f"{code_dir}/{sanitized_name}.py"
    config_file = f"{code_dir}/{sanitized_name}.cfg"

    # We're making some big assumptions here that the file structure / names in RLBotPythonExample will not change.
    os.rename(f"{bot_directory}/{sanitized_name}/python_example/", code_dir)
    os.rename(f"{code_dir}/python_example.py", python_file)
    os.rename(f"{code_dir}/python_example.cfg", config_file)

    # Update the config file to point to the renamed files, and show the correct bot name.
    raw_bot_config = configparser.RawConfigParser()
    raw_bot_config.read(config_file, encoding='utf8')
    agent_config = BaseAgent.base_create_agent_configurations()
    agent_config.parse_file(raw_bot_config)
    agent_config.set_value(BOT_CONFIG_MODULE_HEADER, BOT_NAME_KEY, bot_name)
    agent_config.set_value(BOT_CONFIG_MODULE_HEADER, PYTHON_FILE_KEY, f"{sanitized_name}.py")
    with open(config_file, "w", encoding='utf8') as f:
        f.write(str(agent_config))

    # This is intended to open the example python file in the default system editor for .py files.
    # Hopefully this will be VS Code or notepad++ or something. If it gets executed as a python script, no harm done.
    os.startfile(python_file)

    return config_file
