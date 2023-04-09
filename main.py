import threading

from control.plc_control import x_setting, y_setting, r_setting, shake_setting, temperature_setting
from udp_server import command_server, status_server
from state_machine import state_machine

if __name__ == '__main__':
    state_machine.run()
    # 状态机启动后需要先设置plc基本参数，x轴移动速度，y轴转动速度，r轴正反转圈数，出菜上下行速度，温控上下限温度
    # x_setting(20, 0)
    # y_setting(20, 0.1)
    # r_setting(20, 5, 0.2)
    # shake_setting(10, 5, 0.3)
    # temperature_setting(320, 10, 0.4)
    # state_machine.execute()

    t1 = threading.Thread(target=command_server.run)
    t2 = threading.Thread(target=status_server.run)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
