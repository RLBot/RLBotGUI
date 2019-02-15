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

    # This is not an ideal way of modifying the config file, because:
    # - It uses our custom ConfigObject class, which is limited / buggy, and we should be moving away from it
    # - The ConfigObject class is not capable of 'round-tripping', i.e. if you parse a config file and then
    #   write it again, the comment lines will not be preserved.
    # - It can still write comments, but only if they have a 'description' that has been added programmatically
    #   (see base_create_agent_configurations).
    #
    # One route is to add 'description' items for all the stuff we care about, including the stuff here
    # https://github.com/RLBot/RLBotPythonExample/blob/master/python_example/python_example.cfg#L11-L27
    # so that the resulting file is sortof the same (might have slightly different formatting). That's annoying
    # and hard to maintain though, and again we'd be investing more in this custom config class that I would
    # prefer to get rid of.
    #
    # Alternatives:
    #
    # Use the configobj library https://configobj.readthedocs.io/en/latest/configobj.html
    # - I tried this in https://github.com/IamEld3st/RLBotGUI/commit/a30308940dd5a0e4a45db6ccc088e6e75a9f69f0
    #   which worked well for me, but people reported issues during installation. If we can get the installation
    #   ironed out, it will be a nice solution for modifying cfg files in general.
    #
    # Do a simple find-and-replace in the file
    # - Very crude, but it can be reliable if we use specific commit hashes like I did in
    #   https://github.com/IamEld3st/RLBotGUI/commit/a30308940dd5a0e4a45db6ccc088e6e75a9f69f0
    # - It would get us up and running with the new features until we can figure out a proper config modification
    #   solution.
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
