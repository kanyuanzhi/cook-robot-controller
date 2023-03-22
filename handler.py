import struct
from control.plc_control import *


def unpack_single_instruction(single_instruction: bytes):
    data_type = single_instruction[2:3]
    data_target = struct.unpack(">H", single_instruction[3:5])[0]
    data_action = single_instruction[5:6]
    data_measures = struct.unpack(">I", single_instruction[6:10])[0]
    data_measure_1 = struct.unpack(">B", single_instruction[6:7])[0]
    data_measure_2 = struct.unpack(">B", single_instruction[7:8])[0]
    data_measure_3 = struct.unpack(">B", single_instruction[8:9])[0]
    data_measure_4 = struct.unpack(">B", single_instruction[9:10])[0]
    data_time = struct.unpack(">I", single_instruction[10:14])[0]
    return data_type, data_target, data_action, data_measures, data_measure_1, data_measure_2, data_measure_3, data_measure_4, data_time


class CommandHandler:
    def __init__(self):
        self.data_model = None
        self.data_instruction_count = None
        self.data_content = None

    def handle(self, data: bytes):
        self.data_model = data[7:8]
        self.data_instruction_count = struct.unpack(">H", data[8:10])[0]
        self.data_content = data[14:14 + self.data_instruction_count * 14]
        if self.data_model == b"\x01":
            self._single_command_handle()
        elif self.data_model == b"\x02":
            self._multiple_command_handle()
        else:
            self._plc_instruction_handle()

    def _single_command_handle(self):
        data_type, data_target, data_action, data_measures, data_measure_1, data_measure_2, data_measure_3, data_measure_4, data_time = unpack_single_instruction(
            self.data_content)
        if data_type == b"\x01":
            print("菜盒")
            y_control(b"\x02")  # 两种写法：Y轴复位或Y轴定位到位置0 y_control(b"\x01", 0)
            # todo:Y轴复位延时
            x_control(b"\x01", data_target)
        elif data_type == b"\x02":
            print("水")
        elif data_type == b"\x03":
            print("调料盒")
            y_control(b"\x01", 1)
            # todo:Y轴定位延时
            weight = data_measures  # 分量单位 ml/mg
            time = weight  # 加料分量与加料时长的转换关系,0.01s
            pump_control(data_target, time)
        elif data_type == b"\x04":
            print("火力")
            fire_level = data_measures  # 1~10档，最高加热温度270℃，1档25℃
            temperature = fire_level * 25
            temperature_control(data_action, temperature)
        elif data_type == b"\x05":
            print("翻炒")
            stir_fry_level = data_measures  # 1~5档，R轴最大转速200，1档40转速，正转，不限圈数，炒菜2位(Y轴4号位)
            speed = stir_fry_level * 40
            y_control(b"\x01", 4)
            # todo:需要延时？
            r_control(data_action, data_target, speed, 0)
        elif data_type == b"\x06":
            print("准备炒菜")
            # 全部复位
            x_control(b"\x02")
            y_control(b"\x02")
            r_control(b"\x02")
            temperature_control(b"\x02")
        elif data_type == b"\x07":
            print("出菜")
            y_control(b"\x01", 9)  # 出菜低位(Y轴9号位)
            # todo:Y轴定位延时
            shake_control(5, 5, 3)  # todo： 一键抖菜，抖5次，上行速度5，下行速度3，需要测试
        else:
            print("wrong type")
        pass

    def _multiple_command_handle(self):
        pass

    def _plc_instruction_handle(self):
        data_type, data_target, data_action, data_measures, data_measure_1, data_measure_2, data_measure_3, data_measure_4, data_time = unpack_single_instruction(
            self.data_content)
        if data_type == b"\x20":
            x_control(data_action, data_target)
        elif data_type == b"\x21":
            y_control(data_action, data_target)
        elif data_type == b"\x22":
            r_control(data_action, data_target, data_measure_1, data_measure_2)
        elif data_type == b"\x23":
            pump_control(data_target, data_measures)
        elif data_type == b"\x24":
            shake_control(data_measure_1, data_measure_2, data_measure_3)
        elif data_type == b"\x25":
            temperature_control(data_action, data_measures)
        else:
            print("wrong type")
            return
