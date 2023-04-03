import threading

from control.plc_control import x_setting, y_setting, r_setting, shake_setting, temperature_setting
from udp_server import UDPCommandServer
from state_machine import state_machine

UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT = "/tmp/unixsock_command_client.sock"
UNIX_SOCK_PIPE_PATH_COMMAND_SERVER = "/tmp/unixsock_command_server.sock"
UNIX_SOCK_PIPE_PATH_STATUS_CLIENT = "/tmp/unixsock_status_client.sock"
UNIX_SOCK_PIPE_PATH_STATUS_SERVER = "/tmp/unixsock_status_server.sock"
HOST = "127.0.0.1"
# HOST = "169.254.70.55"
COMMAND_PORT = 9999
STATUS_PORT = 9998

if __name__ == '__main__':
    state_machine.run()
    # 状态机启动后需要先设置plc基本参数，x轴移动速度，y轴转动速度，r轴正反转圈数，出菜上下行速度，温控上下限温度
    # x_setting(20, 0)
    # y_setting(20, 0.1)
    # r_setting(20, 5, 0.2)
    # shake_setting(10, 5, 0.3)
    # temperature_setting(320, 10, 0.4)
    # state_machine.start()

    command_server = UDPCommandServer(UNIX_SOCK_PIPE_PATH_COMMAND_SERVER,
                                      UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT,
                                      COMMAND_PORT)
    t1 = threading.Thread(target=command_server.run)
    t1.start()
    t1.join()
