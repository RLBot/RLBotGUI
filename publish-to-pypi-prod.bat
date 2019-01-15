pip install twine
pip install wheel

RD /S /Q dist

python setup.py sdist bdist_wheel

@rem This requires you to create a .pypirc file like the one described here:
@rem https://github.com/RLBot/RLBot/wiki/Deploying-Changes#first-time-setup

twine upload --repository pypi dist/*