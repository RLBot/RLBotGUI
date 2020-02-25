
def convert_packet_to_dict(ctypes_packet):
    """
    Here we're selectively converting parts of the game tick packet into dict format.
    We're skipping over parts that are currently not needed by the GUI, e.g. boost pad state.
    """
    dict_version = {}
    dict_version['game_ball'] = getdict(ctypes_packet.game_ball)
    dict_version['game_info'] = getdict(ctypes_packet.game_info)
    cars = []
    for i in range(ctypes_packet.num_cars):
        cars.append(getdict(ctypes_packet.game_cars[i]))
    dict_version['game_cars'] = cars
    return dict_version


def getdict(struct):
    """
    This will convert a ctypes struct into a python dict. After that, it can be converted easily to json.
    Taken from https://stackoverflow.com/a/34301571/280852
    """
    result = {}

    def get_value(value):
        if (type(value) not in [int, float, bool]) and not bool(value):
            # it's a null pointer
            value = None
        elif hasattr(value, "_length_") and hasattr(value, "_type_"):
            # Probably an array
            # print value
            value = get_array(value)
        elif hasattr(value, "_fields_"):
            # Probably another struct
            value = getdict(value)
        return value

    def get_array(array):
        ar = []
        for value in array:
            value = get_value(value)
            ar.append(value)
        return ar

    for f in struct._fields_:
        field = f[0]
        value = getattr(struct, field)
        # if the type is not a primitive and it evaluates to False ...
        value = get_value(value)
        result[field] = value
    return result
