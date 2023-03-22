import os.path
import socket
import struct
import sys
import threading
from functools import wraps

from handler import CommandHandler
from packer import Packer

UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT = "/tmp/unixsock_command_client.sock"
UNIX_SOCK_PIPE_PATH_COMMAND_SERVER = "/tmp/unixsock_command_server.sock"
UNIX_SOCK_PIPE_PATH_STATUS_CLIENT = "/tmp/unixsock_status_client.sock"
UNIX_SOCK_PIPE_PATH_STATUS_SERVER = "/tmp/unixsock_status_server.sock"
HOST = "127.0.0.1"
# HOST = "169.254.70.55"
COMMAND_PORT = 9999
STATUS_PORT = 9998


def sendto(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            args[0].server.sendto(result, args[2])
        except Exception as e:
            print(e)
        return result

    return wrapper


class UDPServer:
    def __init__(self, local_path, remote_path, port):
        self.server = None
        self.remote_path = remote_path
        if sys.platform == "linux":
            self.server = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
            if os.path.exists(local_path):
                os.remove(local_path)
            self.addr = local_path
        else:
            self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.addr = (HOST, port)
        self.server.bind(self.addr)
        print(self.__class__.__name__)

    def run(self):
        while True:
            msg, addr = self.server.recvfrom(1024)
            header = msg[0:4].decode("utf-8")
            print(msg)
            if header == "COOK":  # 判断数据包header，如果是COOK，表示为数据包开头，如果不是，则继续
                length = struct.unpack(">I", msg[4:8])[0]
                data = msg[8:8 + length]
                self._process(data, addr)
            else:
                print("packet is not COOK")

    def _process(self, data, addr):
        # override
        pass


class UDPCommandServer(UDPServer):
    @sendto
    def _process(self, data, addr):
        packer = Packer()
        data_header = data[0:3].decode("utf-8")
        command_handler = CommandHandler()
        if data_header == "CCS":  # 接收指令
            # 执行指令，将用户型命令转为一系列PLC型命令或直接处理PLC型指令，查表后写到PLC对应地址
            command_handler.handle(data)

            packer.pack("CCR", b"\x01")  # 返回开始执行指令的信号
        elif data_header == "CIS":  # 接收查询信息，并依据data[7]的值区分查询内容
            if data[7] == 1:  # 查询指令是否可以执行
                # todo:判断指令是否可以执行（如上一条指令还未执行完毕等）
                packer.pack("CIR", b"\x01")  # 若可以，model置1，返回可以执行，准备接收指令；若不可以，model置2（\x02）
        return packer.msg


class UDPStatusServer(UDPServer):
    @sendto
    def _process(self, data, addr):
        packer = Packer()
        packer.pack("CSR", b"\x01")
        return packer.msg

# if __name__ == "__main__":
#     command_server = UDPCommandServer(UNIX_SOCK_PIPE_PATH_COMMAND_SERVER,
#                                       UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT,
#                                       COMMAND_PORT)
#     status_server = UDPStatusServer(UNIX_SOCK_PIPE_PATH_STATUS_SERVER,
#                                     UNIX_SOCK_PIPE_PATH_STATUS_CLIENT,
#                                     STATUS_PORT)
#
#     t1 = threading.Thread(target=command_server.run)
#     t2 = threading.Thread(target=status_server.run)
#
#     t1.start()
#     t2.start()
#
#     t1.join()
#     t2.join()
