from dataclasses import field, dataclass
from math import sqrt, pi
from typing import Optional

from rlbot.training.training import Grade, Pass
from rlbot.utils.game_state_util import GameState, Physics, BallState, Vector3, CarState, Rotator, BoostState
from rlbottraining.common_graders.compound_grader import CompoundGrader
from rlbottraining.common_graders.timeout import FailOnTimeout
from rlbottraining.grading.grader import Grader
from rlbottraining.grading.training_tick_packet import TrainingTickPacket
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import TrainingExercise, Playlist


@dataclass
class PassOnNearBall(Grader):
    """
    Returns a Pass grade once the car is sufficiently close to the ball.
    """

    min_dist_to_pass: float = 200
    car_index: int = 0

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Grade]:
        car = tick.game_tick_packet.game_cars[self.car_index].physics.location
        ball = tick.game_tick_packet.game_ball.physics.location

        dist = sqrt(
            (car.x - ball.x) ** 2 +
            (car.y - ball.y) ** 2
        )
        if dist <= self.min_dist_to_pass:
            return Pass()
        return None


class DriveToBallGrader(CompoundGrader):
    """
    Checks that the car gets to the ball in a reasonable amount of time.
    """
    def __init__(self, timeout_seconds=4.0, min_dist_to_pass=200):
        super().__init__([
            PassOnNearBall(min_dist_to_pass=min_dist_to_pass),
            FailOnTimeout(timeout_seconds),
        ])


@dataclass
class DrivesToBallExercise(TrainingExercise):
    """
    Checks that we drive to the ball when it's in the center of the field.
    """
    grader: Grader = field(default_factory=DriveToBallGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(0, 0, 100),
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, 2000, 0),
                        rotation=Rotator(0, -pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    jumped=False,
                    double_jumped=False,
                    boost_amount=rng.randint(10, 50))
            },
            boosts={i: BoostState(0) for i in range(34)},
        )


def make_default_playlist() -> Playlist:
    exercises = [
        DrivesToBallExercise("Drive-to-ball", grader=DriveToBallGrader(min_dist_to_pass=1000))
    ]

    return exercises
