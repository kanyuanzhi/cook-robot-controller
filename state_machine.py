import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor

# from FX3U_modbus_RTU import sl_rtu
# from XinJie_modbus_RTU import xj_rtu
from Xinjie_modbus_TCP import modbus_tcp, plc_state


def write_work(signal: list):
    # modbus_tcp.config_ser()
    modbus_tcp.write_register(signal)
    # modbus_tcp.ser.close()


def read_work(addresses: list):
    # modbus_tcp.config_ser()
    modbus_tcp.read_register(addresses)
    # modbus_tcp.ser.close()


def write_to_plc(signal: list):
    # t1 = threading.Thread(target=write_work, args=(signal,))
    # t1.execute()
    pass


def read_from_plc():
    # t1 = threading.Thread(target=read_work, args=([('D0', 120), ("HS0", 120)],))
    # t1.execute()
    pass


class StateMachine:
    def __init__(self):
        self.apscheduler = BackgroundScheduler()  # 创建调度器
        self.pool = ThreadPoolExecutor(max_workers=10)  # 创建线程池

        self.machine_state = "idle"  # executing:2/pause:1/idle:0

        self.signals = {}  # 信号字典，{time1:[s1,s2],time2:[s1]}
        self.signal_is_finished = {}  # 信号完成字典， {time1:false,time2:true}
        self.signals_number = 0  # 信号总数

        self.executing_initial_time = 0  # 状态机“执行”状态的初始时间
        self.executing_run_time = 0  # 状态机“执行”状态的运行时间
        self.pause_time = 0  # 状态机暂停时间

        self.r_state = {  # R轴状态
            "running": 0,  # 0停止，1旋转
            "mode": 0  # 0默认，1正转，2反转，3正反转
        }

        print(self.__class__.__name__)

    def add_signal(self, signal, execute_time, is_immediate=False):
        execute_time *= 10  # 执行时间控制精度0.1s
        if is_immediate:  # 立即执行的指令
            self.pool.submit(write_work, args=(signal,))  # 写plc
        else:  # 不是立即执行的指令，按时间顺序执行
            if self.machine_state != "idle":
                print("machine is busy now!")
                return False
            if execute_time not in self.signals:
                self.signals[execute_time] = [signal]
                self.signal_is_finished[execute_time] = False
            else:
                self.signals[execute_time].append(signal)
            self.signals_number += 1

    def check_state(self):  # 检查状态，当前是否有任务在运行
        pass

    def get_r_state(self):
        return self.r_state

    def set_r_state(self, running, mode):
        self.r_state["running"] = running
        self.r_state["mode"] = mode

    def execute(self):  # 指令注入完毕后，调用此方法开始执行
        if len(self.signals) == 0:
            print("没有指令需要执行")
            return
        self.machine_state = "executing"  # 状态机进入执行指令状态
        plc_state.set("machine_state", 2)
        self.apscheduler.add_job(self.__write, args=(), trigger="interval", seconds=0.001, id="write")  # 添加一个写任务
        self.executing_initial_time = time.time()  # 指令执行的初始时间设置为当前时间

    def pause(self):  # 只暂停写任务
        self.pause_time = time.time()
        self.machine_state = "pause"
        plc_state.set("machine_state", 1)

    def run(self):
        self.apscheduler.add_job(self.__read, args=(), trigger="interval", seconds=1, id="read")  # 添加一个读任务
        self.apscheduler.start()

    def __write_work(self):
        current_time = time.time()
        self.executing_run_time = int(
            int(current_time * 1000 - self.executing_initial_time * 1000) / 100)  # 执行时间控制精度0.1s
        plc_state.set("time", self.executing_run_time)
        if self.executing_run_time in self.signal_is_finished \
                and self.signal_is_finished[self.executing_run_time] is False:
            # 执行状态的运行时间在信号字典中，且信号未被执行
            self.signal_is_finished[self.executing_run_time] = True  # 信号设置为完成
            for signal in self.signals[self.executing_run_time]:
                # 执行一个时间点上的多条信号
                print("{}:指令{}，执行时刻{}".format(time.time(), signal, self.executing_run_time / 10))

                self.pool.submit(write_work, signal)  # 写plc

                self.signals_number -= 1  # 信号数量减1
                if self.signals_number == 0:
                    # 信号全部执行完毕
                    self.machine_state = "idle"  # 状态机进入挂起状态
                    plc_state.set("machine_state", 0)  # 状态机进入挂起状态
                    self.signals = {}  # 信号字典清空
                    self.signal_is_finished = {}  # 信号完成字典清空
                    self.apscheduler.get_job("write").remove()  # 移除写任务
                    plc_state.set("time", 0)  # 执行时间置零
                    print("执行完毕\n" + "*" * 50)
        return

    def __write(self):
        try:
            self.pool.submit(self.__write_work)
        except Exception as e:
            print(e)

    def __read(self):
        try:
            self.pool.submit(read_work, ([('DS0', 120), ("HS0", 120)]))
        except Exception as e:
            print(e)


state_machine = StateMachine()  # 全局状态机

if __name__ == "__main__":
    state_machine.run()

    state_machine.add_signal("s1", 0)
    state_machine.add_signal("s2", 2)
    state_machine.add_signal("s3", 5)
    state_machine.add_signal("s4", 10)
    print(state_machine.signals)

    state_machine.execute()

    while True:
        # print(time.time())
        time.sleep(1)
