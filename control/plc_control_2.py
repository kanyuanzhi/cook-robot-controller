y_position = {
    0: "DD200",
    1: "DD202",
    2: "DD204",
    3: "DD206",
    4: "DD208",
    5: "DD210",
    6: "DD212",
    7: "DD214",
    8: "DD216",
    9: "DD218",
}


def y_control(action: bytes, position: int = 0):
    if action == b"\x01":
        signal = [("DD10", 1), ("DD12", position)]
        watch_address = ["DD100"]
        watch_value = [y_position[position]]
    elif action == b"\x02":
        signal = [("DD0", 1)]
        watch_address = ["DD100"]
        watch_value = [y_position[0]]
    else:
        raise NameError("action error")
    return signal, watch_address, watch_value


x_position = {
    0: "DD250",
    1: "DD252",
    2: "DD254",
    3: "DD256",
    4: "DD258",
    5: "DD260",
    6: "DD262",
    7: "DD264",
    8: "DD266",
    9: "DD268",
}


def x_control(action: bytes, position: int = 0):
    if action == b"\x01":
        signal = [("DD20", 1), ("DD22", position)]
        watch_address = ["DD102"]
        watch_value = [x_position[position]]
    elif action == b"\x02":
        signal = [("DD2", 1)]
        watch_address = ["DD102"]
        watch_value = [x_position[0]]
    else:
        raise NameError("action error")
    return signal, watch_address, watch_value


def temperature_control(action: bytes, temperature: int = 0, target_temperature):
    if action == b"\x01":
        signal = [("DD70", 1), ("DS72", temperature)]
        print("温控{}℃，{}s".format(temperature / 10, execute_time))
    elif action == b"\x02":
        signal = [("DD70", 1), ("DS72", 0)]
        print("温控0℃，{}s".format(execute_time))
    else:
        raise NameError("wrong action")
    return [signal], [execute_time], is_immediate