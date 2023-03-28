from control.plc_control import *


def ingredient_control(slot_num: int, execute_time: int = 0):
    print("菜盒")
    y_control(b"\x02", execute_time=execute_time)  # 两种写法：Y轴复位或Y轴定位到位置0 y_control(b"\x01", 0)
    # todo:Y轴复位延时2s
    x_control(b"\x01", slot_num, execute_time=execute_time + 2)


def water_control(weight: int, execute_time: int = 0):
    print("水")
    y_control(b"\x01", 1, execute_time=execute_time)
    # todo:Y轴定位延时2秒
    time = weight  # 加料分量与加料时长的转换关系,1ml/mg~0.01s
    # pump_control(9, time, execute_time=execute_time + 2)


def seasoning_control(slot_num: int, weight: int, execute_time: int = 0):
    print("调料盒")
    y_control(b"\x01", 1, execute_time=execute_time)
    # todo:Y轴定位延时2秒
    time = weight  # 加料分量与加料时长的转换关系,1ml/mg~0.01s
    # pump_control(slot_num, time, execute_time=execute_time + 2)


def fire_control(action: bytes, fire_level: int = 0, execute_time: int = 0):
    print("火力")
    # fire_level：1~10档，最高加热温度300℃，1档30℃
    temperature = fire_level * 300
    temperature_control(action, temperature, execute_time=execute_time)


def stir_fry_control(action: bytes, stir_fry_level: int = 0, execute_time: int = 0):
    print("翻炒")
    # stir_fry_level：1~5档，R轴最大转速200，1档40转速，正转，不限圈数，炒菜2位(Y轴4号位)
    speed = stir_fry_level * 40
    # 停止翻炒需要Y轴复位？
    y_control(b"\x01", 4, execute_time=execute_time)
    # todo:需要延时？
    r_control(action, 1, speed, execute_time=execute_time)


def prepare_control(execute_time: int = 0):
    print("准备炒菜")
    # 全部复位
    x_control(b"\x02", execute_time=execute_time)
    y_control(b"\x02", execute_time=execute_time + 1)
    r_control(b"\x02", execute_time=execute_time + 2)
    temperature_control(b"\x02", execute_time=execute_time + 3)


def dish_out_control(execute_time: int = 0):
    print("出菜")
    y_control(b"\x01", 9, execute_time=execute_time)  # 出菜低位(Y轴9号位)
    # todo:Y轴定位延时2秒
    shake_control(5, execute_time=execute_time + 2)  # todo： 一键抖菜，抖5次，需要测试