from rlbot.gateway_util import NetworkingRole
from rlbot.matchconfig.loadout_config import LoadoutConfig
from rlbot.matchconfig.match_config import PlayerConfig, MatchConfig, MutatorConfig
from rlbot.parsing.incrementing_integer import IncrementingInteger
from rlbot.setup_manager import SetupManager
from rlbot.utils.structures.bot_input_struct import PlayerInput
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator

sm: SetupManager = None


def create_player_config(bot, human_index_tracker: IncrementingInteger):
    player_config = PlayerConfig()
    player_config.bot = bot['type'] in ('rlbot', 'psyonix')
    player_config.rlbot_controlled = bot['type'] in ('rlbot', 'party_member_bot')
    player_config.bot_skill = bot['skill']
    player_config.human_index = 0 if player_config.bot else human_index_tracker.increment()
    player_config.name = bot['name']
    player_config.team = int(bot['team'])
    if 'path' in bot and bot['path']:
        player_config.config_path = bot['path']
    return player_config


def spawn_car_in_showroom(loadout_config: LoadoutConfig, team: int):
    match_config = MatchConfig()
    match_config.game_mode = 'Soccer'
    match_config.game_map = 'Mannfield'
    match_config.instant_start = True
    match_config.existing_match_behavior = 'Continue And Spawn'
    match_config.networking_role = NetworkingRole.none

    bot_config = PlayerConfig()
    bot_config.bot = True
    bot_config.rlbot_controlled = True
    bot_config.team = team
    bot_config.name = "Showroom"
    bot_config.loadout_config = loadout_config

    match_config.player_configs = [bot_config]
    match_config.mutators = MutatorConfig()
    match_config.mutators.boost_amount = 'Unlimited'
    match_config.mutators.match_length = 'Unlimited'

    global sm
    if sm is None:
        sm = SetupManager()
    sm.connect_to_game()
    sm.load_match_config(match_config)
    sm.start_match()
    player_input = PlayerInput()
    player_input.boost = True
    player_input.throttle = 1
    player_input.steer = 1
    sm.game_interface.update_player_input(player_input, 0)
    sm.game_interface.set_game_state(GameState(cars={0: CarState(physics=Physics(
        location=Vector3(0, -1136, 0),
        velocity=Vector3(2300, 0, 0),
        angular_velocity=Vector3(0, 0, 3),
        rotation=Rotator(0, 0, 0)
    ))}))


def start_match_helper(bot_list, match_settings):
    print(bot_list)
    print(match_settings)

    match_config = MatchConfig()
    match_config.game_mode = match_settings['game_mode']
    match_config.game_map = match_settings['map']
    match_config.skip_replays = match_settings['skip_replays']
    match_config.instant_start = match_settings['instant_start']
    match_config.enable_lockstep = match_settings['enable_lockstep']
    match_config.existing_match_behavior = match_settings['match_behavior']
    match_config.mutators = MutatorConfig()

    mutators = match_settings['mutators']
    match_config.mutators.match_length = mutators['match_length']
    match_config.mutators.max_score = mutators['max_score']
    match_config.mutators.overtime = mutators['overtime']
    match_config.mutators.series_length = mutators['series_length']
    match_config.mutators.game_speed = mutators['game_speed']
    match_config.mutators.ball_max_speed = mutators['ball_max_speed']
    match_config.mutators.ball_type = mutators['ball_type']
    match_config.mutators.ball_weight = mutators['ball_weight']
    match_config.mutators.ball_size = mutators['ball_size']
    match_config.mutators.ball_bounciness = mutators['ball_bounciness']
    match_config.mutators.boost_amount = mutators['boost_amount']
    match_config.mutators.rumble = mutators['rumble']
    match_config.mutators.boost_strength = mutators['boost_strength']
    match_config.mutators.gravity = mutators['gravity']
    match_config.mutators.demolish = mutators['demolish']
    match_config.mutators.respawn_time = mutators['respawn_time']

    human_index_tracker = IncrementingInteger(0)
    match_config.player_configs = [create_player_config(bot, human_index_tracker) for bot in bot_list]

    global sm
    if sm is not None:
        try:
            sm.shut_down(kill_all_pids=True)
        except Exception as e:
            print(e)

    sm = SetupManager()
    sm.early_start_seconds = 5
    sm.connect_to_game()
    sm.load_match_config(match_config)
    sm.launch_early_start_bot_processes()
    sm.start_match()
    sm.launch_bot_processes()
    # Note that we are not calling infinite_loop because that is not compatible with the way eel works!
    # Instead we will reproduce the important behavior from infinite_loop inside this file.


def do_infinite_loop_content():
    if sm is not None and sm.has_started:
        sm.try_recieve_agent_metadata()


def hot_reload_bots():
    if sm is not None:
        sm.reload_all_agents()


def shut_down():
    if sm is not None:
        sm.shut_down(time_limit=5, kill_all_pids=True)
    else:
        print("There gotta be some setup manager already")

