import setuptools

__version__ = '0.0.163'

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot_gui',
    packages=setuptools.find_namespace_packages(exclude=['*logos*'], include=["rlbot_gui*"]),
    python_requires='>=3.11',
    # It actually requires 'gevent', 'eel', 'PyQt5', but that messes up the install for some people and we're
    # already bundling those in the pynsist installer.
    # We'll go ahead and list some packages needed by bots in the bot pack, though.
    install_requires=[
        'numba',
        'scipy',
        'numpy',
        'RLUtilities',  # Used by Snek
        'websockets',  # Needed for scratch bots
        'selenium',  # Needed for scratch bots
        'PyQt5'  # Used for settings and file pickers currently.
        ],
    version=__version__,
    description='A streamlined user interface for RLBot.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='RLBot Community',
    author_email='rlbotofficial@gmail.com',
    url='https://github.com/RLBot/RLBotGUI',
    keywords=['rocket-league'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    include_package_data=True,
    package_data={
        'rlbot_gui': [
            '**/*.json',
        ]
    },
)
