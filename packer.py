import json
import struct
from time import time
from Xinjie_modbus_TCP import plc_state

HEADER = "COOK"
COMMAND_DATA_HEADER = "CCS"
INQUIRY_DATA_HEADER = "CIS"
STATE_REQUEST_DATA_HEADER = "CSS"
STATE_RESPONSE_DATA_HEADER = "CSR"


def get_state(number: str):
    if number[0:2] == "DD":
        return plc_state.get("DS" + str(int(number[2:]) + 1)) * 65536 + plc_state.get(number)
    elif number[0:2] == "DS":
        return plc_state.get(number)
    elif number[0:2] == "HD":
        return plc_state.get("HS" + str(int(number[2:]) + 1)) * 65536 + plc_state.get(number)
    elif number[0:2] == "HS":
        return plc_state.get(number)
    else:
        return plc_state.get(number)


# HEADER DATA_LENGTH DATA_INFO DATA1 DATA2 DATA3 ...
class CommandResponsePacker:
    count = 1

    def __init__(self):
        self.msg = HEADER.encode()  # HEADER, 4 bytes
        self.data_info = b""
        self.data_content = b""
        CommandResponsePacker.count += 1

    def pack(self, data_header: str, model: bytes):
        self.data_info += data_header.encode()  # DATA_HEADER, 3 bytes
        self.data_info += struct.pack(">I", self.count)  # DATA_NO, 4 bytes
        self.data_info += model  # DATA_MODEL, 1 byte
        self.data_info += b"\x00\x00"
        self.data_info += struct.pack(">I", int(time()))  # DATA_DATETIME, 4 bytes


class StateResponsePacker:
    count = 1

    def __init__(self):
        self.msg = HEADER.encode()  # HEADER, 4 bytes
        self.data_info = b""
        self.data_content = b""
        StateResponsePacker.count += 1

    def pack(self, data_header: str, model: bytes):
        self.data_info += data_header.encode()  # DATA_HEADER, 3 bytes
        self.data_info += struct.pack(">I", self.count)  # DATA_NO, 4 bytes
        self.data_info += model  # DATA_MODEL, 1 byte
        self.data_info += b"\x00\x00"
        self.data_info += struct.pack(">I", int(time()))  # DATA_DATETIME, 4 bytes

        state = {
            "time": get_state("time"),
            "machine_state": get_state("machine_state"),
            # "time": 127,

            "y_reset_control_word": get_state("DD0"),
            "y_set_control_word": get_state("DD10"),
            "y_set_target_position": get_state("DD12"),
            "y_set_real_position": get_state("DD100"),
            "y_set_total_distance": get_state("DD104"),
            "y_set_rotate_speed": get_state("HS110"),

            "x_reset_control_word": get_state("DD2"),
            "x_set_control_word": get_state("DD20"),
            "x_set_target_position": get_state("DD22"),
            "x_set_real_position": get_state("DD102"),
            "x_set_total_distance": get_state("DD106"),
            "x_set_move_speed": get_state("HS112"),

            "r_control_word": get_state("DD4"),
            "r_rotate_mode": get_state("DD6"),
            "r_rotate_speed": get_state("HS100"),
            "r_rotate_number": get_state("HS104"),

            "shake_control_word": get_state("DD30"),
            "shake_current_number": get_state("DD32"),
            "shake_total_number": get_state("HS34"),
            "shake_up_speed": get_state("HS114"),
            "shake_down_speed": get_state("HS117"),

            "liquid_pump_control_word": get_state("DD40"),
            "liquid_pump_number": get_state("DD42"),
            "liquid_pump_time": get_state("HS124"),

            "water_pump_control_word": get_state("DD50"),
            "water_pump_number": get_state("DD52"),
            "water_pump_time": get_state("HS126"),

            "solid_pump_control_word": get_state("DD60"),
            "solid_pump_number": get_state("DD62"),
            "solid_pump_time": get_state("HS128"),

            "temperature_control_word": get_state("DD70"),
            "temperature_target_number": get_state("DS72"),
            "temperature_current_number": get_state("DS74"),
            "temperature_up_number": get_state("DS76"),
            "temperature_down_number": get_state("DS77"),
            "temperature_warning": get_state("DS78"),
            "temperature_infrared_number": get_state("DS80"),

            "emergency": get_state("DD90"),
            # "emergency": 9999,
        }

        for key in state:
            self.data_content += struct.pack(">H", state[key])
        self.msg += struct.pack(">I", 14 + len(state) * 2)  # DATA_LENGTH, 4 bytes
        self.msg += self.data_info
        self.msg += self.data_content
