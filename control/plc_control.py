from functools import wraps


def write(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = []
        try:
            result = func(*args, **kwargs)
            for address in result:
                print(address)
        except Exception as e:
            print(e)
        return result

    return wrapper


@write
def x_control(action: bytes, position: int = 0):
    if action == b"\x01":
        addresses = [("D20", 1), ("D22", position)]
        print("X轴定位{}".format(position))
    elif action == b"\x02":
        addresses = [("D2", 1)]
        print("X轴复位")
    else:
        raise NameError("wrong action")
    return addresses


@write
def y_control(action: bytes, position: int = 0):
    if action == b"\x01":
        addresses = [("D10", 1), ("D12", position)]
        print("Y轴定位{}".format(position))
    elif action == b"\x02":
        addresses = [("D0", 1)]
        print("Y轴复位")
    else:
        raise NameError("wrong action")
    return addresses


@write
def r_control(action: bytes, mode: int = 0, speed: int = 0, circles: int = 0):
    if action == b"\x01":
        addresses = [("D4", 1), ("D6", mode), ("HD100", speed), ("HD104", circles)]
        print("R轴{}转，速度{}，圈数{}".format("正" if mode == 1 else "反" if mode == 2 else "正反", speed, circles))
    elif action == b"\x02":
        addresses = [("D4", 0)]
        print("R轴停转")
    else:
        raise NameError("wrong action")
    return addresses


@write
def pump_control(pump_number: int, time: int):
    addresses = [("D40", 1), ("D42", pump_number), ("D44", time)]
    print("供料泵{}号打开，时长{}秒".format(pump_number, time / 100))
    return addresses


@write
def shake_control(shake_count: int, up_speed: int, down_speed: int):
    addresses = [("D30", 1), ("D34", shake_count), ("HD114", up_speed), ("HD116", down_speed)]
    print("抖菜{}次，上行速度{}，下行速度{}".format(shake_count, up_speed, down_speed))
    return addresses


@write
def temperature_control(action: bytes, temperature: int = 0):
    if action == b"\x01":
        addresses = [("D50", 1), ("D52", temperature)]
        print("温控{}℃".format(temperature))
    elif action == b"\x02":
        addresses = [("D50", 1), ("D52", 0)]
        print("温控0℃")
    else:
        raise NameError("wrong action")
    return addresses
