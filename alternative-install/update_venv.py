import os

path = os.path.join(os.getenv('LocalAppData'), 'RLBotGUIX\\venv\\pyvenv.cfg')

with open(path, 'r') as file:
    config = file.readlines()

config[0] = "home = " + os.path.join(os.getenv('LocalAppData'), 'RLBotGUIX\\Python37') + "\n"

with open(path, 'w') as file:
    file.writelines(config)
