from rlbot_gui.rlbottrainingpack.json_pack import JSONPack

def make_default_playlist():
  return JSONPack(__file__.replace('.py', '.simple_exercises.json'))
