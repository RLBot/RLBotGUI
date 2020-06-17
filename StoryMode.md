Rocket League Story Mode
=========================

# Status

- First match works end to end
- Post-first match UI is being fleshed out
    - A map is shown! 
    - Lock/open/done status can be shown and calculated
    - A side bar is created to show details but needs to be populated
    - Upgrades are listed and respect save state and most take effect
    - A declarative framework to describe challenges is created
- Remaining:
    - Need to implement teammates
        - Need to implement customizaiton options
    - Need to test rumble upgrade
    - Need to implement recharging boost
    - Need to implement additional "winConditions" and "limitations"
    - Need to update bots.json with the additional bots we want


# Developer notes

- Save structure is defined in python in `story/runner.py`
- Rules for winning a level are defined in Python
- Rules for going from level to level (what level becomes unlocked) are defined in JavaScript