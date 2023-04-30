from control.plc_control import *


def ingredient_control(slot_num: int, execute_time: float = 0):
    print("****菜盒****执行时刻{}s".format(execute_time))
    y_control(b"\x01", 1, execute_time=execute_time)  # 两种写法：Y轴复位或Y轴定位到位置0 y_control(b"\x01", 0)
    # todo:Y轴复位延时3s
    x_control(b"\x01", slot_num, execute_time=execute_time + 3)
    # todo:加完料之后，判断下一个加料时间，若紧接着则Y轴保持，若很久或不再加料，则Y轴回到原位置


def water_control(weight: int, execute_time: float = 0):
    print("****水****执行时刻{}s".format(execute_time))
    # y_control(b"\x01", 2, execute_time=execute_time)
    time = weight * 10 / 6.4  # 加料分量与加料时长的转换关系,1ml/mg~0.1s
    water_pump_control(1, time, execute_time=execute_time)
    # todo:加完料之后，判断下一个加料时间，若紧接着则Y轴保持，若很久或不再加料，则Y轴回到原位置


def seasoning_control(slot_num: int, weight: int, execute_time: float = 0):
    print("****调料盒****执行时刻{}s".format(execute_time))
    y_control(b"\x01", 2, execute_time=execute_time)
    # todo:Y轴定位延时3秒
    if slot_num in [1, 2, 3, 4, 5, 6]:  # 液体泵
        time = weight * 1000 / 6.4  # 加料分量与加料时长的转换关系,1ml/g~0.001s
        liquid_pump_control(slot_num, time, execute_time=execute_time + 3)
        # todo:加完料之后，判断下一个加料时间，若紧接着则Y轴保持，若很久或不再加料，则Y轴回到原位置
    elif slot_num in [7, 8]:  # 固体泵
        time = weight * 10 / 10  # 加料分量与加料时长的转换关系,10g~1s
        pump_number = 1 if slot_num == 7 else 2  # 7对应1号固体泵，8对应2号固体泵
        solid_pump_control(pump_number, time, execute_time=execute_time + 3)
        # todo:加完料之后，判断下一个加料时间，若紧接着则Y轴保持，若很久或不再加料，则Y轴回到原位置
    else:
        print(slot_num)
        raise NameError("错误，泵号超出1~8")


def fire_control(action: bytes, fire_level: int = 0, execute_time: float = 0, is_immediate=False):
    print("****火力****执行时刻{}s".format(execute_time))
    # fire_level：1~10档，加热温度30~230℃，1档20℃
    if fire_level == 0:
        temperature = 0
    else:
        temperature = (fire_level - 1) * 200 + 300
    temperature_control(action, temperature, execute_time=execute_time, is_immediate=is_immediate)


def stir_fry_control(action: bytes, stir_fry_level: int = 0, execute_time: float = 0):
    print("****翻炒****执行时刻{}s".format(execute_time))
    # stir_fry_level：1~5档，R轴最大转速2000，1档350转速，正转，炒菜2位(Y轴4号位)
    speed = stir_fry_level * 350
    if speed == 0:
        # 停止翻炒需要Y轴复位？
        r_control(b"\x02", execute_time=execute_time)
    else:
        y_control(b"\x01", 4, execute_time=execute_time)  # Y轴定位4号位（炒菜2位）
        # todo:需要延时？
        r_control(action, 1, speed, execute_time=execute_time)


def prepare_control(execute_time: float = 0):
    print("****准备炒菜****执行时刻{}s".format(execute_time))
    # 全部复位
    # x_control(b"\x02", execute_time=execute_time)
    # y_control(b"\x02", execute_time=execute_time)
    r_control(b"\x02", execute_time=execute_time)
    temperature_control(b"\x02", execute_time=execute_time)


def dish_out_control(execute_time: float = 0):
    print("****出菜****执行时刻{}s".format(execute_time))
    # y_control(b"\x01", 9, execute_time=execute_time)  # 出菜低位(Y轴9号位)
    shake_control(5, execute_time=execute_time)  # todo： 一键抖菜，抖5次，需要测试


def finish_control(execute_time: float = 0):
    print("****结束****执行时刻{}s".format(execute_time))
    r_control(b"\x02", execute_time=execute_time)  # R轴停转
    temperature_control(b"\x02", execute_time=execute_time)  # 停火


def reset0_control(execute_time: float = 0, is_immediate=False):
    print("****复位0****执行时刻{}s".format(execute_time))
    x_control(b"\x02", execute_time=execute_time, is_immediate=is_immediate)  # X轴定位0号位（原点）
    y_control(b"\x02", execute_time=execute_time, is_immediate=is_immediate)  # Y轴定位2号位（接料2位）
    r_control(b"\x02", execute_time=execute_time, is_immediate=is_immediate)  # R轴停转
    temperature_control(b"\x02", execute_time=execute_time, is_immediate=is_immediate)  # 停火


def reset1_control(execute_time: float = 0):
    print("****复位1****执行时刻{}s".format(execute_time))
    x_control(b"\x01", 1, execute_time=execute_time)  # X轴定位1号位（上菜位）
    y_control(b"\x01", 2, execute_time=execute_time)  # Y轴定位2号位（接料2位）


def wash_control(execute_time: float = 0):
    print("****清洗****执行时刻{}s".format(execute_time))
    y_control(b"\x01", 1, execute_time=execute_time)  # Y轴定位3号位（炒菜1位）
    r_control(b"\x01", 3, 1000, execute_time=execute_time)  # R轴正反转，速度1000
    water_pump_control(1, 400, execute_time=execute_time + 5)  # 水泵40秒
    temperature_control(b"\x01", 500, execute_time=execute_time + 5)  # 加热50℃
    temperature_control(b"\x01", 0, execute_time=execute_time + 20)  # 15秒后停止加热
    r_control(b"\x02", execute_time=execute_time + 45)  # R轴停转
    y_control(b"\x01", 7, execute_time=execute_time + 45)  # Y轴定位7号位（倒水位）
    y_control(b"\x01", 1, execute_time=execute_time + 50)  # Y轴定位1号位（接料1位）
