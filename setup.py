import setuptools

__version__ = '0.0.17'

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='rlbot_gui',
    packages=setuptools.find_packages(),
    # It actually requires 'gevent', 'eel', 'PyQt5', but that messes up the install for some people and we're
    # already bundling those in the pynsist installer.
    install_requires=[],
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
)
