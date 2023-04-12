import os.path
import socket
import struct
import sys
import threading
from functools import wraps

from handler import CommandHandler
from packer import CommandResponsePacker, StateResponsePacker

UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT = "/tmp/unixsock_command_client.sock"
UNIX_SOCK_PIPE_PATH_COMMAND_SERVER = "/tmp/unixsock_command_server.sock"
UNIX_SOCK_PIPE_PATH_STATUS_CLIENT = "/tmp/unixsock_status_client.sock"
UNIX_SOCK_PIPE_PATH_STATUS_SERVER = "/tmp/unixsock_status_server.sock"
HOST = "127.0.0.1"
# HOST = "192.168.6.10"
# HOST = "169.254.70.55"
COMMAND_CLIENT_PORT = 10010
COMMAND_SERVER_PORT = 10011
STATUS_CLIENT_PORT = 10012
STATUS_SERVER_PORT = 10013

COMMAND_DATA_HEADER = "CCS"
INQUIRY_DATA_HEADER = "CIS"
STATE_REQUEST_DATA_HEADER = "CSS"
STATE_RESPONSE_DATA_HEADER = "CSR"


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
    def __init__(self, local_path, remote_path, local_port, remote_port):
        self.server = None
        if sys.platform == "linux11":
            self.server = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
            if os.path.exists(local_path):
                os.remove(local_path)
            self.addr = local_path
            self.remote_addr = remote_path
        else:
            self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.addr = (HOST, local_port)
            self.remote_addr = (HOST, remote_port)
        self.server.bind(self.addr)
        print(self.addr)
        print(self.__class__.__name__)

    def run(self):
        while True:
            msg, addr = self.server.recvfrom(1024)
            header = msg[0:4].decode("utf-8")
            # print(msg)
            if header == "COOK":  # 判断数据包header，如果是COOK，表示为数据包开头，如果不是，则继续
                length = struct.unpack(">I", msg[4:8])[0]
                data = msg[8:8 + length]
                self._process(data, self.remote_addr)
            else:
                print("packet is not COOK")

    def _process(self, data, addr):
        # override
        pass


class UDPCommandServer(UDPServer):
    def __init__(self, local_path, remote_path, local_port, remote_port):
        super().__init__(local_path, remote_path, local_port, remote_port)

    @sendto
    def _process(self, data, addr):
        packer = CommandResponsePacker()
        data_header = data[0:3].decode("utf-8")
        command_handler = CommandHandler()
        if data_header == COMMAND_DATA_HEADER:  # 接收指令
            # 执行指令，将用户型命令转为一系列PLC型命令或直接处理PLC型指令，查表后写到PLC对应地址
            try:
                command_handler.handle(data)
            except Exception as e:
                print(e.args)
            packer.pack("CCR", b"\x01")  # 返回开始执行指令的信号
        elif data_header == INQUIRY_DATA_HEADER:  # 接收查询信息，并依据data[7]的值区分查询内容
            if data[7] == 1:  # 查询指令是否可以执行
                # todo:判断指令是否可以执行（如上一条指令还未执行完毕等）
                packer.pack("CIR", b"\x01")  # 若可以，model置1，返回可以执行，准备接收指令；若不可以，model置2（\x02）
        return packer.msg


class UDPStatusServer(UDPServer):
    def __init__(self, local_path, remote_path, local_port, remote_port):
        super().__init__(local_path, remote_path, local_port, remote_port)

    @sendto
    def _process(self, data, addr):
        packer = StateResponsePacker()
        packer.pack(STATE_RESPONSE_DATA_HEADER, b"\x01")
        # print(data)
        # print(len(packer.msg))
        return packer.msg


command_server = UDPCommandServer(UNIX_SOCK_PIPE_PATH_COMMAND_SERVER,
                                  UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT,
                                  COMMAND_SERVER_PORT, COMMAND_CLIENT_PORT)
status_server = UDPStatusServer(UNIX_SOCK_PIPE_PATH_STATUS_SERVER,
                                UNIX_SOCK_PIPE_PATH_STATUS_CLIENT,
                                STATUS_SERVER_PORT, STATUS_CLIENT_PORT)

# if __name__ == "__main__":
#     command_server = UDPCommandServer(UNIX_SOCK_PIPE_PATH_COMMAND_SERVER,
#                                       UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT,
#                                       COMMAND_CLIENT_PORT)
#     status_server = UDPStatusServer(UNIX_SOCK_PIPE_PATH_STATUS_SERVER,
#                                     UNIX_SOCK_PIPE_PATH_STATUS_CLIENT,
#                                     STATUS_PORT)
#
#     t1 = threading.Thread(target=command_server.run)
#     t2 = threading.Thread(target=status_server.run)
#
#     t1.execute()
#     t2.execute()
#
#     t1.join()
#     t2.join()
