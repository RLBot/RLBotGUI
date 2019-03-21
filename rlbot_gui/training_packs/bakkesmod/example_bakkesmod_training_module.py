from rlbottraining.common_exercises.bakkesmod_import.bakkesmod_importer import exercises_from_bakkesmod_playlist

def make_default_playlist():
    # You can browse playlists here:
    # https://workshop.bakkesmod.com/maps/playlists/
    #
    # Once you found a playlist you like, you can copy its ID from the URL.
    # For example:
    # https://workshop.bakkesmod.com/maps/playlist/quJfnUJf22/
    #                                                |
    #                                                v
    return exercises_from_bakkesmod_playlist('quJfnUJf22')
