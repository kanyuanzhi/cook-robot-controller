from functools import wraps
from state_machine import state_machine


def write(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = []
        try:
            signals, execute_times, is_immediate = func(*args, **kwargs)
            for index, signal in enumerate(signals):
                state_machine.add_signal(signal, execute_times[index], is_immediate)
        except Exception as e:
            print(e)
        return result

    return wrapper


@write
def x_control(action: bytes, position: int = 0, execute_time: float = 0, is_immediate=False):
    if action == b"\x01":
        signal = [("DD20", 1), ("DD22", position)]
        print("X轴定位{}，{}s".format(position, execute_time))
    elif action == b"\x02":
        signal = [("DD2", 1)]
        print("X轴复位，{}s".format(execute_time))
    else:
        raise NameError("wrong action")
    return [signal], [execute_time], is_immediate


@write
def y_control(action: bytes, position: int = 0, execute_time: float = 0, is_immediate=False):
    if action == b"\x01":
        signal = [("DD10", 1), ("DD12", position)]
        print("Y轴定位{}，{}s".format(position, execute_time))
    elif action == b"\x02":
        signal = [("DD0", 1)]
        print("Y轴复位，{}s".format(execute_time))
    else:
        raise NameError("wrong action")
    return [signal], [execute_time], is_immediate


@write
def r_control(action: bytes, mode: int = 0, speed: int = 0, execute_time: float = 0, is_immediate=False):
    if action == b"\x01":
        r_state = state_machine.get_r_state()
        if r_state["running"] == 0:
            signal = [("DD4", 1), ("DD6", mode), ("HS100", speed)]
        elif r_state["mode"] == mode:  # 同模式下直接设置旋转速度
            signal = [("HS100", speed)]
        else:  # 改变旋转模式，需要先复位再设置
            signal1 = [("DD4", 0), ("DD6", 0)]
            signal2 = [("DD4", 1), ("DD6", mode), ("HS100", speed)]
            state_machine.set_r_state(1, mode)
            print("R轴{}转，速度{}，{}s".format("正" if mode == 1 else "反" if mode == 2 else "正反", speed, execute_time))
            return [signal1, signal2], [execute_time, execute_time + 0.1], is_immediate  # 复位后延时0.1秒再设置
        state_machine.set_r_state(1, mode)
        print("R轴{}转，速度{}，{}s".format("正" if mode == 1 else "反" if mode == 2 else "正反", speed, execute_time))
    elif action == b"\x02":
        signal = [("DD4", 0), ("DD6", 0)]
        state_machine.set_r_state(0, 0)
        print("R轴停转，{}s".format(execute_time))
    else:
        raise NameError("wrong action")
    return [signal], [execute_time], is_immediate


@write
def liquid_pump_control(pump_number: int, time: int, execute_time: float = 0, is_immediate=False):
    signal = [("DD40", 1), ("DD42", pump_number), ("HS124", time)]
    print("液体泵{}号打开，时长{}s，{}s".format(pump_number, time / 1000, execute_time))
    return [signal], [execute_time], is_immediate


@write
def solid_pump_control(pump_number: int, time: int, execute_time: float = 0, is_immediate=False):
    signal = [("DD60", 1), ("DD62", pump_number), ("HS128", time)]
    print("固体泵{}号打开，时长{}s，{}s".format(pump_number, time / 10, execute_time))
    return [signal], [execute_time], is_immediate


@write
def water_pump_control(pump_number: int, time: int, execute_time: float = 0, is_immediate=False):
    signal = [("DD50", 1), ("DD52", pump_number), ("HS126", time)]
    print("水泵{}号打开，时长{}s，{}s".format(pump_number, time / 10, execute_time))
    return [signal], [execute_time], is_immediate


@write
def shake_control(shake_count: int, execute_time: float = 0, is_immediate=False):
    signal = [("DD30", 1), ("DD34", shake_count)]
    print("抖菜{}次，{}s".format(shake_count, execute_time))
    return [signal], [execute_time], is_immediate


@write
def temperature_control(action: bytes, temperature: int = 0, execute_time: float = 0, is_immediate=False):
    if action == b"\x01":
        signal = [("DD70", 1), ("DS72", temperature)]
        print("温控{}℃，{}s".format(temperature / 10, execute_time))
    elif action == b"\x02":
        signal = [("DD70", 1), ("DS72", 0)]
        print("温控0℃，{}s".format(execute_time))
    else:
        raise NameError("wrong action")
    return [signal], [execute_time], is_immediate


@write
def x_setting(speed: int = 0, execute_time: float = 0):
    signal = [("HS112", speed)]
    print("设置X轴移动速度{}，{}s".format(speed, execute_time))
    return [signal], [execute_time]


@write
def y_setting(speed: int = 0, execute_time: float = 0):
    signal = [("HS110", speed)]
    print("设置Y轴转动速度{}，{}s".format(speed, execute_time))
    return [signal], [execute_time]


@write
def r_setting(speed: int = 0, circles: int = 0, execute_time: float = 0):
    signal = [("HS100", speed), ("HS104", circles)]
    print("设置R轴旋转速度{}，正反转圈数{}，{}s".format(speed, circles, execute_time))
    return [signal], [execute_time]


@write
def shake_setting(up_speed: int = 0, down_speed: int = 0, execute_time: float = 0):
    signal = [("HS114", up_speed), ("HS116", down_speed)]
    print("设置抖菜上行速度{}，下行速度{}，{}s".format(up_speed, down_speed, execute_time))
    return [signal], [execute_time]


@write
def temperature_setting(high_temperature: int = 0, low_temperature: int = 0, execute_time: float = 0):
    signal = [("DS76", high_temperature), ("DS77", low_temperature)]
    print("设置温度上限值{}，温度下限值{}，{}s".format(high_temperature, low_temperature, execute_time))
    return [signal], [execute_time]
