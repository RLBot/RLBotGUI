import json
from importlib._bootstrap import module_from_spec
from importlib._bootstrap_external import spec_from_file_location
from os import path, listdir

from rlbottraining.common_exercises.bakkesmod_import.bakkesmod_importer import (
    exercises_from_bakkesmod_playlist,
    BakkesmodImportedExercise
)
from rlbottraining.training_exercise import Playlist

from rlbot_gui.rlbottrainingpack.json_pack import JSONPack


def import_pack(folder_abs_path: str) -> Playlist:
    if "packdata.json" in listdir(folder_abs_path):
        path_ = path.join(folder_abs_path, "packdata.json")
        with open(path_) as fp:
            data = json.load(fp)
        type_ = data.get("format", "bakkes")
        if type_ == "json":
            return JSONPack(path_)
        elif type_ == "python":
            spec = spec_from_file_location("trainer", path.join(folder_abs_path,
                                                                data.get("file", "trainer.py")))
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)
            if not hasattr(mod, "make_default_playlist"):
                raise Exception("Training module should have a `make_default_playlist` attribute.")
            return mod.make_default_playlist()
        elif type_ in ("bakkes", "bakkesmod"):
            if "playlist_id" in data:
                return exercises_from_bakkesmod_playlist(data["playlist_id"])
            else:
                return [BakkesmodImportedExercise(shot_id) for shot_id in data["shots"]]
        else:
            raise Exception(f"Invalid pack format: '{type_}'")
    else:
        raise Exception(f"No packdata.json file found in folder: `{folder_abs_path}`")
