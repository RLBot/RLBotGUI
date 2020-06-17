Rocket League Story Mode
=========================

# Status

- First match works end to end
- Post-first match UI is being fleshed out
    - A map is shown! 
    - Lock/open/done status can be shown and calculated
    - A side bar is created to show details but needs to be populated
    - Upgrades are listed and respect save state
- Remaining:
    - We need to come up with descriptions of each challenge and implement each match's setup
    - Need to implement usage of purchases
    - Need to implement teammates


# Developer notes

- Save structure is defined in python in `story/runner.py`
- Rules for winning a level are defined in Python
- Rules for going from level to level (what level becomes unlocked) are defined in JavaScript