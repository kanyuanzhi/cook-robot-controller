import struct
from control.plc_control import *
from control.user_control import *
from state_machine import state_machine


def unpack_single_instruction(single_instruction: bytes):
    data_type = single_instruction[2:3]
    data_target = struct.unpack(">H", single_instruction[3:5])[0]
    data_action = single_instruction[5:6]
    data_measures = struct.unpack(">I", single_instruction[6:10])[0]
    data_measure_left = struct.unpack(">H", single_instruction[6:8])[0]
    data_measure_right = struct.unpack(">H", single_instruction[8:10])[0]
    data_measure_1 = struct.unpack(">B", single_instruction[6:7])[0]
    data_measure_2 = struct.unpack(">B", single_instruction[7:8])[0]
    data_measure_3 = struct.unpack(">B", single_instruction[8:9])[0]
    data_measure_4 = struct.unpack(">B", single_instruction[9:10])[0]
    data_time = struct.unpack(">I", single_instruction[10:14])[0]
    return data_type, data_target, data_action, data_measures, data_measure_left, data_measure_right, \
           data_measure_1, data_measure_2, data_measure_3, data_measure_4, data_time


class CommandHandler:
    def __init__(self):
        self.data_model = None
        self.data_instruction_count = None
        self.data_content = None

    def handle(self, data: bytes):
        print(state_machine.machine_state)
        if state_machine.machine_state != "idle":
            print("machine is busy now!")
            return
        self.data_model = data[7:8]
        self.data_instruction_count = struct.unpack(">H", data[8:10])[0]
        self.data_content = data[14:14 + self.data_instruction_count * 14]
        if self.data_model == b"\x01":
            self._single_command_handle(self.data_content)  # data_content大小 14
        elif self.data_model == b"\x02":
            self._multiple_command_handle(self.data_content)  # data_content大小 14*n
        else:
            self._plc_instruction_handle(self.data_content)  # data_content大小 14
        state_machine.execute()

    @staticmethod
    def _single_command_handle(data_content):
        data_type, data_target, data_action, data_measures, data_measure_left, data_measure_right, data_measure_1, \
        data_measure_2, data_measure_3, data_measure_4, data_time = unpack_single_instruction(data_content)
        if data_type == b"\x01":
            ingredient_control(data_target, execute_time=data_time)
        elif data_type == b"\x02":
            water_control(data_measures, execute_time=data_time)
        elif data_type == b"\x03":
            seasoning_control(data_target, data_measures, execute_time=data_time)
        elif data_type == b"\x04":
            fire_control(data_action, data_measures, execute_time=data_time)
        elif data_type == b"\x05":
            stir_fry_control(data_action, data_measures, execute_time=data_time)
        elif data_type == b"\x06":
            prepare_control(execute_time=data_time)
        elif data_type == b"\x07":
            dish_out_control(execute_time=data_time)
        elif data_type == b"\x08":
            finish_control(execute_time=data_time)
        else:
            print("wrong type")
            return

    def _multiple_command_handle(self, data_content):
        for i in range(self.data_instruction_count):
            self._single_command_handle(data_content[14 * i:14 * i + 14])

    @staticmethod
    def _plc_instruction_handle(data_content):
        data_type, data_target, data_action, data_measures, data_measure_left, data_measure_right, data_measure_1, \
        data_measure_2, data_measure_3, data_measure_4, data_time = unpack_single_instruction(data_content)
        if data_type == b"\x20":
            x_control(data_action, data_target, execute_time=data_time)
        elif data_type == b"\x21":
            y_control(data_action, data_target, execute_time=data_time)
        elif data_type == b"\x22":
            r_control(data_action, data_target, data_measures, execute_time=data_time)
        elif data_type == b"\x23":
            liquid_pump_control(data_target, data_measures, execute_time=data_time)
        elif data_type == b"\x24":
            solid_pump_control(data_target, data_measures, execute_time=data_time)
        elif data_type == b"\x25":
            water_pump_control(data_target, data_measures, execute_time=data_time)
        elif data_type == b"\x26":
            shake_control(data_measures, execute_time=data_time)
        elif data_type == b"\x27":
            temperature_control(data_action, data_measures, execute_time=data_time)

        elif data_type == b"\x50":
            x_setting(data_measures, execute_time=data_time)
        elif data_type == b"\x51":
            y_setting(data_measures, execute_time=data_time)
        elif data_type == b"\x52":
            r_setting(data_measure_left, data_measure_right, execute_time=data_time)
        elif data_type == b"\x53":
            shake_setting(data_measure_left, data_measure_right, execute_time=data_time)
        elif data_type == b"\x54":
            temperature_setting(data_measure_left, data_measure_right, execute_time=data_time)

        else:
            print("wrong type")
            return
