import struct
from time import time
from XinJie_modbus_RTU import plc_status

# x盒状态D22
# y位D12
# 旋转中D4 旋转模式D6 旋转圈数HD100
# 出中D30

HEADER = "COOK"
COMMAND_DATA_HEADER = "CCR"
INQUIRY_DATA_HEADER = "CRR"


def double_process(number: str):
    if number[0:2] == "DD":
        return plc_status.get("DD" + str(int(number[2:]) + 1)) * 65536 + plc_status.get(number)
    elif number[0:2] == "SD":
        return plc_status.get(number)
    elif number[0:2] == "HD":
        return plc_status.get("HD" + str(int(number[2:]) + 1)) * 65536 + plc_status.get(number)


# HEADER DATA_LENGTH DATA_INFO DATA1 DATA2 DATA3 ...
class Packer:
    count = 1

    def __init__(self):
        self.msg = HEADER.encode()  # HEADER, 4 bytes
        self.data_info = b""
        Packer.count += 1

    def pack(self, data_header: str, model: bytes):
        self.msg += struct.pack(">I", 14)  # DATA_LENGTH, 4 bytes

        self.data_info += data_header.encode()  # DATA_HEADER, 3 bytes
        self.data_info += struct.pack(">I", self.count)  # DATA_NO, 4 bytes
        self.data_info += model  # DATA_MODEL, 1 byte
        self.data_info += b"\x00\x00"
        self.data_info += struct.pack(">I", int(time()))  # DATA_DATETIME, 4 bytes

        self.msg += self.data_info

        y_reset_control_word = double_process("DD0")
        y_set_control_word = double_process("DD10")
        y_set_target_position = double_process("DD12")
        y_set_real_position = double_process("DD100")
        y_set_total_distance = double_process("DD104")
        y_set_rotate_speed = double_process("HD110")

        x_reset_control_word = double_process("DD2")
        x_set_control_word = double_process("DD20")
        x_set_target_position = double_process("DD22")
        x_set_real_position = double_process("DD102")
        x_set_total_distance = double_process("DD106")
        x_set_move_speed = double_process("HD112")
