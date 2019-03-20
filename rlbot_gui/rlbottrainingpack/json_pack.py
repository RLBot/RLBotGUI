import json
from enum import Enum

from rlbottraining.training_exercise import Playlist


from rlbot_gui.rlbottrainingpack.exercises import Striker, Goalie


class Graders(Enum):
    GOALIE = Goalie
    SCORER = Striker


class JSONPack(list, Playlist):
    def __init__(self, filename: str):
        super().__init__()
        with open(filename) as fp:
            data = json.load(fp)

        assert isinstance(data, dict), "JSON Pack should be an Object"

        training_type = data.get("type", "")
        assert training_type.lower() in ("goalie", "scorer"), \
            f"Invalid/missing `type` property in training pack: {filename}"

        entries = data.get("entries")

        for entry in entries:
            ex_cls = getattr(Graders, training_type.upper()).value
            ex = ex_cls(entry["ball"],
                        entry["cars"],
                        entry.get("boosts"),
                        entry.get("timeout"),
                        data.get("description"))
            self.append(ex)
