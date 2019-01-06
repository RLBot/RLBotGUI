@echo off

@rem Unfortunately, the exe produced by this command spazzes out when we try to start a match, don't know why yet.
@rem You need to pip install pyinstaller before you can use this.

python -m eel run.py gui --onefile --hidden-import=rlbot
