import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler


# from FX3U_modbus_RTU import sl_rtu
# from XinJie_modbus_RTU import xj_rtu


def write_to_plc(addresses: list):
    print(addresses)


def read_from_plc():
    print(time.time())


class StateMachine:
    def __init__(self):
        self.apscheduler = BackgroundScheduler()
        self.states = {}  # {time1:[s1,s2],time2:[s1]}
        self.state_is_finished = {}  # {time1:false,time2:true}
        self.initial_time = 0
        self.states_number = 0

        self.machine_status = "idle"  # running/pause/idle
        self.execute_time = 0
        print(self.__class__.__name__)

    def add_state(self, signal, execute_time):
        if self.machine_status != "idle":
            print("machine is busy now!")
            return False
        if execute_time not in self.states:
            self.states[execute_time] = [signal]
            self.state_is_finished[execute_time] = False
        else:
            self.states[execute_time].append(signal)
        self.states_number += 1
        return True

    def check_state(self):  # 检查状态，当前是否有任务在运行
        pass

    def set_initial_time(self):
        self.initial_time = int(time.time())

    def execute(self):
        if self.machine_status == "running":
            current_time = time.time()
            self.execute_time = int(int(current_time * 1000 - self.initial_time * 1000) / 1000)
            if self.execute_time in self.state_is_finished and self.state_is_finished[self.execute_time] is False:
                self.state_is_finished[self.execute_time] = True
                for signal in self.states[self.execute_time]:
                    print("{}:指令{}，执行时刻{}".format(time.time(), signal, self.execute_time))
                    # rtu.write_register(signal)
                    # t1 = threading.Thread(target=xj_rtu.write_register, args=(signal,))
                    # t1.start()

                    self.states_number -= 1
                    if self.states_number == 0:
                        self.machine_status = "idle"
                        self.states = {}
                        self.state_is_finished = {}
                        print("执行完毕")
                        print("*" * 50)

    def read(self):
        try:
            pass
        # t1 = threading.Thread(target=sl_rtu.read_register, args=([['D0', 80]],))
        # t2 = threading.Thread(target=rtu.read_register, args=([['D0', 50]],))
        # t1.start()
        # t2.start()
        except Exception as e:
            print(e)

    def start(self):
        if len(self.states) == 0:
            print("没有指令需要执行")
            return
        self.initial_time = time.time()
        self.machine_status = "running"

    def pause(self):
        self.machine_status = "pause"

    def run(self):
        self.apscheduler.add_job(self.execute, args=(), trigger="interval", seconds=0.01)
        # self.apscheduler.add_job(self.read, trigger="interval", seconds=0.2)
        self.apscheduler.start()


state_machine = StateMachine()

if __name__ == "__main__":
    state_machine.run()

    state_machine.add_state("s1", 0)
    state_machine.add_state("s2", 2)
    state_machine.add_state("s3", 5)
    state_machine.add_state("s4", 10)
    print(state_machine.states)

    state_machine.start()

    while True:
        # print(time.time())
        time.sleep(1)
