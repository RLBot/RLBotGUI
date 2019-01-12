# RLBot-Electron

## Dev Environment Setup

### Prerequisites

- Python 3.6+

### Setup

1. In a command prompt, run `pip install -r requirements.txt`
2. Run `python run.py`

### Deployment

You can build an installer executable for users to download.

1. Follow https://pynsist.readthedocs.io/en/latest/index.html to get NSIS installed.
2. Run `pip install pynsist`
3. Run `pynsist installer.cfg`

Find the resulting executable in build\nsis.
