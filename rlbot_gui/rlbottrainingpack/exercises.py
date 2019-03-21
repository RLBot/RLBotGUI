from math import pi
from pathlib import Path
from secrets import token_hex
from typing import Dict, Any, Optional, List, Union

from rlbot.matchconfig.match_config import PlayerConfig, Team
from rlbot.utils.game_state_util import GameState, Physics, BallState, Vector3, Rotator, CarState, BoostState
from rlbottraining.common_exercises.common_base_exercises import StrikerExercise, GoalieExercise
from rlbottraining.common_graders.compound_grader import CompoundGrader
from rlbottraining.common_graders.goal_grader import (
    PassOnGoalForAllyTeam, StrikerGrader, PassOnBallGoingAwayFromGoal,
    GoalieGrader
)
from rlbottraining.match_configs import make_default_match_config
from rlbottraining.rng import SeededRandomNumberGenerator

from rlbot_gui.rlbottrainingpack.math_parser import parse_item


V0 = Vector3(0, 0, 0)
R0 = Rotator(0, pi/2, 0)


def as_cls(cls, arg):
    if not isinstance(arg, cls):
        return cls(*arg)
    return arg


class JSONExercise:
    boosts: list
    description: str

    def __init__(self):
        self.name = self.description + token_hex(5)
        self.match_config = make_default_match_config()
        while len(self.boosts) < 34:
            self.boosts.append(0)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=as_cls(Vector3,
                                parse_item(rng,
                                           self.ball.get("location", V0))),
                velocity=as_cls(Vector3,
                                parse_item(rng,
                                           self.ball.get("velocity", V0))),
                angular_velocity=as_cls(Vector3,
                                        parse_item(rng,
                                                   self.ball.get("angular_velocity", V0))),
                rotation=as_cls(Rotator,
                                parse_item(rng,
                                           self.ball.get("rotation", R0))),
            )),
            cars={
                i: CarState(
                    physics=Physics(
                        location=as_cls(Vector3,
                                        parse_item(rng,
                                                   car.get("location", V0))),
                        velocity=as_cls(Vector3,
                                        parse_item(rng,
                                                   car.get("velocity", V0))),
                        angular_velocity=as_cls(Vector3,
                                                parse_item(rng,
                                                           car.get("angular_velocity", V0))),
                        rotation=as_cls(Rotator,
                                        parse_item(rng,
                                                   car.get("rotation", R0))),
                    ),
                    jumped=parse_item(rng, car.get("jumped", False)),
                    double_jumped=parse_item(rng, car.get("double_jumped", False)),
                    boost_amount=parse_item(rng, car.get("boost_amount", 0))
                )
                for i, car in enumerate(self.cars)
            },
            boosts={
                i: BoostState(parse_item(rng, v))
                for i, v in enumerate(self.boosts)
            }
        )


class Striker(StrikerExercise, JSONExercise):
    def __init__(self, ball_physics: Dict[str, Any], cars: List[Dict[str, Any]],
                 boosts: Optional[List[Union[str, int]]] = None, timeout: Optional[float] = None,
                 description: Optional[str] = None):
        self.description = description or "Striker Exercise"
        self.ball = ball_physics
        self.cars = cars
        self.boosts = boosts or []
        self.timeout = timeout or 10.0
        self.grader = StrikerGrader(self.timeout) if self.timeout > 0 else PassOnGoalForAllyTeam(0)
        JSONExercise.__init__(self)

    def make_game_state(self, rng: SeededRandomNumberGenerator):
        return JSONExercise.make_game_state(self, rng)


class Goalie(GoalieExercise, JSONExercise):
    def __init__(self, ball_physics: Dict[str, Any], cars: List[Dict[str, Any]],
                 boosts: Optional[List[Union[str, int]]] = None, timeout: Optional[float] = None,
                 description: Optional[str] = None):
        self.description = description or "Goalie Exercise"
        self.ball = ball_physics
        self.cars = cars
        self.boosts = boosts or []
        self.timeout = timeout or 10.0
        self.grader = (
            GoalieGrader(self.timeout)
            if self.timeout > 0
            else CompoundGrader([
                PassOnBallGoingAwayFromGoal(0),
                PassOnGoalForAllyTeam(0)
            ])
        )
        JSONExercise.__init__(self)

    def make_game_state(self, rng: SeededRandomNumberGenerator):
        return JSONExercise.make_game_state(self, rng)
