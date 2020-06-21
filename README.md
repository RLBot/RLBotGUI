# Rocket League Story Mode

This project used RLBot and RLBotGui to provide a Story Mode for
Rocket League. The story UI runs in your browser and it can
start games to continue with the story.

Here are some images from the UI.


Works on Windows and Linux

## Status

The current Story Mode is fully functioning. Your saves are persisted,
you can recruit players, you can purchase upgrades on your way
to taking over more cities.

Here are things that can use additional work/feedback:

### Packaging/Deployment

- One possibility worth discussing is if this project could be packaged
as part of RLBotGui
- If not, its probably worth removing the unused code from RLBotGui and
package it on its own so people don't have to run it through python

### Features to add

- Adding support for "bot personas". Currently bots are just added
    with their bot names and using their default appearance. If a bot is
    used in different cities, they look the same. We should instead have 
    different "persona" in each city with different names and different looks.
- Recruited teammate customization: Players should be able to customize
    their teammates' looks.
- Should other types of challenges be added? Other types of stats to track?

### Bot recommendations

The current selection of bots was chosen somewhat arbitrarily. Recommendation
on bots that fit specific challenges would be great. Additionally, ideas
for challenges that use particular skills of bots would be valuable too.

### UI Improvements

- Adding more animation and sound when a user succeeds might be good
- The CSS and HTML layout is pretty ad-hoc right now. Cleaning that up
would be good.
- A different map that has more RL feel would be very cool. Also ideas
for keeping the map extendible would be good too.


## How to run

Currently you have to clone this repo and run through there. If you have 
RLBotGUI cloned, you can just add this repo as a remote and switch to that.

If you are doing a fresh clone:

```
$ pip -r requirements.txt
$ python run.py
```

This will load the RLBotGui website, you can go inside and click on "Add -> Download BotPack".
This will download all the bots that are used i nthe story mode.

After that you can click on the "Story Mode" button on the top right.


## How to Customize

Story Mode is primarily described in two JSON files:
  - `rlbot_gui/story/bots.json`: This dictates what bots are available and how they are configured
  - `rlbot_guid/story/challenges.json`: This dictates the challenges in each city
  and what the goals and restrictions are of each challenge. It also picks which
  bots to use for each level.
    - Note that if you are adding new cities, there is more UI work involved.
