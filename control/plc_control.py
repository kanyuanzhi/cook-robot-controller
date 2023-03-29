from functools import wraps
from state_machine import state_machine


def write(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = []
        try:
            signals, execute_times = func(*args, **kwargs)
            for index, signal in enumerate(signals):
                state_machine.add_state(signal, execute_times[index])
        except Exception as e:
            print(e)
        return result

    return wrapper


@write
def x_control(action: bytes, position: int = 0, execute_time: int = 0):
    if action == b"\x01":
        signal = [("D20", 1), ("D22", position)]
        print("X轴定位{}".format(position))
    elif action == b"\x02":
        signal = [("D2", 1)]
        print("X轴复位")
    else:
        raise NameError("wrong action")
    return [signal], [execute_time]


@write
def y_control(action: bytes, position: int = 0, execute_time: int = 0):
    if action == b"\x01":
        signal = [("D10", 1), ("D12", position)]
        print("Y轴定位{}".format(position))
    elif action == b"\x02":
        signal = [("D0", 1)]
        print("Y轴复位")
    else:
        raise NameError("wrong action")
    return [signal], [execute_time]


@write
def r_control(action: bytes, mode: int = 0, speed: int = 0, execute_time: int = 0):
    if action == b"\x01":
        r_state = state_machine.get_r_state()
        if r_state["running"] == 0:
            signal = [("D4", 1), ("D6", mode), ("HD100", speed)]
        elif r_state["mode"] == mode:  # 同模式下直接设置旋转速度
            signal = [("HD100", speed)]
        else:  # 改变旋转模式，需要先复位再设置
            signal1 = [("D4", 0), ("D6", 0)]
            signal2 = [("D4", 1), ("D6", mode), ("HD100", speed)]
            state_machine.set_r_state(1, mode)
            print("R轴{}转，速度{}".format("正" if mode == 1 else "反" if mode == 2 else "正反", speed))
            return [signal1, signal2], [execute_time, execute_time + 0.1]  # 复位后延时0.1秒再设置
        state_machine.set_r_state(1, mode)
        print("R轴{}转，速度{}".format("正" if mode == 1 else "反" if mode == 2 else "正反", speed))
    elif action == b"\x02":
        signal = [("D4", 0), ("D6", 0)]
        state_machine.set_r_state(0, 0)
        print("R轴停转")
    else:
        raise NameError("wrong action")
    return [signal], [execute_time]


@write
def liquid_pump_control(pump_number: int, time: int, execute_time: int = 0):
    signal = [("D40", 1), ("D42", pump_number), ("HD124", time)]
    print("液体泵{}号打开，时长{}秒".format(pump_number, time / 1000))
    return [signal], [execute_time]


@write
def solid_pump_control(pump_number: int, time: int, execute_time: int = 0):
    signal = [("D60", 1), ("D62", pump_number), ("HD128", time)]
    print("固体泵{}号打开，时长{}秒".format(pump_number, time / 10))
    return [signal], [execute_time]


@write
def water_pump_control(pump_number: int, time: int, execute_time: int = 0):
    signal = [("D50", 1), ("D52", pump_number), ("HD126", time)]
    print("水泵{}号打开，时长{}秒".format(pump_number, time / 10))
    return [signal], [execute_time]


@write
def shake_control(shake_count: int, execute_time: int = 0):
    signal = [("D30", 1), ("D34", shake_count)]
    print("抖菜{}次".format(shake_count))
    return [signal], [execute_time]


@write
def temperature_control(action: bytes, temperature: int = 0, execute_time: int = 0):
    if action == b"\x01":
        signal = [("D70", 1), ("D72", temperature)]
        print("温控{}℃".format(temperature / 10))
    elif action == b"\x02":
        signal = [("D70", 1), ("D72", 0)]
        print("温控0℃")
    else:
        raise NameError("wrong action")
    return [signal], [execute_time]


@write
def x_setting(speed: int = 0, execute_time: int = 0):
    signal = [("HD112", speed)]
    print("设置X轴移动速度{}".format(speed))
    return [signal], [execute_time]


@write
def y_setting(speed: int = 0, execute_time: int = 0):
    signal = [("HD110", speed)]
    print("设置Y轴转动速度{}".format(speed))
    return [signal], [execute_time]


@write
def r_setting(speed: int = 0, circles: int = 0, execute_time: int = 0):
    signal = [("HD100", speed), ("HD104", circles)]
    print("设置R轴旋转速度{}，正反转圈数{}".format(speed, circles))
    return [signal], [execute_time]


@write
def shake_setting(up_speed: int = 0, down_speed: int = 0, execute_time: int = 0):
    signal = [("HD114", up_speed), ("HD116", down_speed)]
    print("设置抖菜上行速度{}，下行速度{}".format(up_speed, down_speed))
    return [signal], [execute_time]


@write
def temperature_setting(high_temperature: int = 0, low_temperature: int = 0, execute_time: int = 0):
    signal = [("D76", high_temperature), ("D77", low_temperature)]
    print("设置温度上限值{}，温度下限值{}".format(high_temperature, low_temperature))
    return [signal], [execute_time]
