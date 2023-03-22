import struct
from time import time

HEADER = "COOK"
COMMAND_DATA_HEADER = "CCR"
INQUIRY_DATA_HEADER = "CRR"


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
