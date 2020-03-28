from rlbot.utils.game_state_util import GameState, BallState, CarState, GameInfoState, Physics, Vector3, Rotator


def dict_to_game_state(state_dict):
    gs = GameState()
    if 'ball' in state_dict:
        gs.ball = BallState()
        if 'physics' in state_dict['ball']:
            gs.ball.physics = dict_to_physics(state_dict['ball']['physics'])
    if 'cars' in state_dict:
        gs.cars = {}
        for index, car in state_dict['cars'].items():
            car_state = CarState()
            if 'physics' in car:
                car_state.physics = dict_to_physics(car['physics'])
            if 'boost_amount' in car:
                car_state.boost_amount = car['boost_amount']
            gs.cars[int(index)] = car_state
    if 'game_info' in state_dict:
        gs.game_info = GameInfoState()
        if 'paused' in state_dict['game_info']:
            gs.game_info.paused = state_dict['game_info']['paused']
        if 'world_gravity_z' in state_dict['game_info']:
            gs.game_info.world_gravity_z = state_dict['game_info']['world_gravity_z']
        if 'game_speed' in state_dict['game_info']:
            gs.game_info.game_speed = state_dict['game_info']['game_speed']
    if 'console_commands' in state_dict:
        gs.console_commands = state_dict['console_commands']
    return gs


def dict_to_physics(physics_dict):
    phys = Physics()
    if 'location' in physics_dict:
        phys.location = dict_to_vec(physics_dict['location'])
    if 'velocity' in physics_dict:
        phys.velocity = dict_to_vec(physics_dict['velocity'])
    if 'angular_velocity' in physics_dict:
        phys.angular_velocity = dict_to_vec(physics_dict['angular_velocity'])
    if 'rotation' in physics_dict:
        phys.rotation = dict_to_rot(physics_dict['rotation'])
    return phys


def dict_to_vec(v):
    vec = Vector3()
    if 'x' in v:
        vec.x = v['x']
    if 'y' in v:
        vec.y = v['y']
    if 'z' in v:
        vec.z = v['z']
    return vec


def dict_to_rot(r):
    rot = Rotator()
    if 'pitch' in r:
        rot.pitch = r['pitch']
    if 'yaw' in r:
        rot.yaw = r['yaw']
    if 'roll' in r:
        rot.roll = r['roll']
    return rot
