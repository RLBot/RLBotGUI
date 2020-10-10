py -m pip install twine
py -m pip install wheel

RD /S /Q dist

py setup.py sdist bdist_wheel

@rem This requires you to create a .pypirc file like the one described here:
@rem https://github.com/RLBot/RLBot/wiki/Deploying-Changes#first-time-setup

twine upload --repository pypi dist/*
