#!/usr/bin/env python
# -*- coding:utf-8 -*-
from binascii import *
import crcmod  # crcmod为专门用于crc校验的库
import serial
import os
import struct
import time
import configparser


class PLCState:
    def __init__(self):
        self._status = {}

    def set(self, number, value):
        # todo：加锁？
        self._status[number] = value

    def get(self, number):
        if number not in self._status:
            return 0
        else:
            return self._status[number]


class modbus_RTU_communication():
    def __init__(self):
        self.ser = None
        self.config_ser()

    # 如果连接串口成功会返回串口实例，连接失败会返回False
    def config_ser(self):
        # 在传递键值对数据时，会将键名全部转化为小写
        conf = configparser.ConfigParser()
        if os.path.isfile("config.ini"):
            conf.read("config.ini")
            comNo = conf.get("modbus_RTU_settings", "comNo")
            baud = int(conf.get("modbus_RTU_settings", "baud"))
            timeout = int(conf.get("modbus_RTU_settings", "timeout"))
            bytesize = int(conf.get("modbus_RTU_settings", "bytesize"))
            stopbits = int(conf.get("modbus_RTU_settings", "stopbits"))
            parity = {"None": serial.PARITY_NONE, "EVEN": serial.PARITY_EVEN, "ODD": serial.PARITY_ODD}
            parity = parity[conf.get("modbus_RTU_settings", "parity")]
        else:
            conf.add_section('modbus_RTU_settings')
            conf.set('modbus_RTU_settings', 'comNo', 'COM5')
            conf.set('modbus_RTU_settings', "baud", '9600')
            conf.set('modbus_RTU_settings', 'timeout', '1')
            conf.set('modbus_RTU_settings', 'bytesize', '8')
            conf.set('modbus_RTU_settings', 'stopbits', '1')
            conf.set('modbus_RTU_settings', 'parity', 'None')
            conf.set('frequency', 'Intervals', '5')
            conf.write(open('config.ini', 'w'))
        try:
            self.ser = serial.Serial(port=comNo, baudrate=baud, bytesize=bytesize, parity=parity, stopbits=stopbits,
                                     timeout=timeout)
            # 发送连接测试命令

        except BaseException as e:
            # print("串口连接失败,请核对连线及COM口编号:", e)
            self.ser = None
            return False

    # 生成CRC16-MODBUS校验码
    def crc16Add(self, read):
        crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        data = read.replace(" ", "")  # 消除空格
        readcrcout = hex(crc16(unhexlify(data))).upper()
        str_list = list(readcrcout)
        # print(str_list)
        if len(str_list) == 5:
            str_list.insert(2, '0')  # 位数不足补0，因为一般最少是5个
        crc_data = "".join(str_list)  # 用""把数组的每一位结合起来  组成新的字符串
        # print(crc_data)
        read = read.strip() + crc_data[4:] + crc_data[2:4]  # 把源代码和crc校验码连接起来
        CRC16 = crc_data[4:] + crc_data[2:4]  # 单纯的CRC校验码，已经将高低字节调换
        # print('CRC16校验:', crc_data[4:] + ' ' + crc_data[2:4])
        # print(read)
        return CRC16

    def read_register(self, datas):
        '''
        一次读n个数据寄存器D：站号；功能码03；寄存器地址；寄存器个数；CRC
        读D1000、D1001：01 03 03 E8 00 02 44 7B

        Returns:
        写入成功，返回True
        '''
        if len(datas) == 0:
            pass
        else:
            salveNum = b'02'  # 站号；0x表示十六进制的int型变量，\x表示十六进制的字符型变量
            # print('0x{:02X}'.format(int(salveNum)))
            order = b'03'  # 功能码，寄存器读
            result = []  # 读取的返回结果，以[[D0, value0], [D1, value1]...]给出

            for data in datas:
                resultSingle = []
                model = data[0][0].upper()

                registerNum = int(data[1])  # 读取的寄存器个数
                registerNumhex = hex(registerNum)[2:].zfill(4)
                registerNumhex = (registerNumhex.upper()).encode('UTF-8')

                if model == 'D':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                    num = int(data[0][1:])  # 寄存器的十进制编号
                    address = hex(num)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')

                elif model == 'H':  # HD寄存器对应modbus地址十进制41088~47231，十六进制A080~B87F
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num + 41088)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                else:
                    print("输入有误")
                    return

                messageList = salveNum + order + address + registerNumhex
                messageStr = str(messageList, encoding="utf-8")
                crc16str = self.crc16Add(messageStr)
                crc16 = crc16str.encode('UTF-8')

                # cmd12 = ('0x{:02X}'.format(int(salveNum))).encode('UTF-8')#从'1'变成'\x01'
                CMD1 = 0x010300010001D5CA  # 报文示例，读D0
                # a = struct.pack(">B", int(salveNum, base=16))
                # a += struct.pack(">B", int(order, base=16))
                # a += struct.pack(">H", int(address, base=16))
                # a += struct.pack(">H", int(registerNumhex, base=16))
                # a += struct.pack(">H", int(crc16, base=16))
                # self.ser.write(a)

                CMD = int.to_bytes(int(salveNum, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(order, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(address, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(registerNumhex, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(crc16, base=16), 2, byteorder='big')
                self.ser.write(CMD)

                data_size = registerNum * 2
                buffer_size = 5 + data_size
                buffer = self.ser.read(buffer_size)
                bufferHex = buffer.hex()
                # print(bufferHex)
                for i in range(registerNum):
                    registerValue = int(bufferHex[(6 + 4 * i):(6 + 4 * i + 4)], base=16)
                    resultSingle.append([model + str(num + i), registerValue])  # data[0]
                    plc_state.set(model + str(num + i), registerValue)
                result.append(resultSingle)
                print(result)
        return result

    def write_register(self, datas):
        '''
        单个数据寄存器D写：站号；功能码06；寄存器地址；数据内容；CRC
        D2写入K5000：02 06 00 02 13 88 25 5C

        多个数据寄存器D写：站号；功能码10；寄存器地址；寄存器个数；字节数；数据内容；CRC
        D0、D1、D2分别写入1、2、3：02 10 00 00 00 03 06 00 01 00 02 00 03 3A 81

        数据寄存器D地址：K0~20479，H0~4FFF
        掉电保持数据寄存器HD0~HD999地址：K41088~47231， HA080~B87F
        Returns:
        写入成功，返回True
        '''
        if len(datas) == 0:
            pass
        else:
            salveNum = b'02'  # 站号；0x表示十六进制的int型变量，\x表示十六进制的字符型变量
            # print('0x{:02X}'.format(int(salveNum)))
            order = b'06'  # 功能码，单个寄存器写，暂时没有同时写多个寄存器

            for data in datas:
                model = data[0][0:2].upper()

                registerNum = int(data[1])  # 需要写入的十进制数
                registerNumhex = hex(registerNum)[2:].zfill(4)
                registerNumhex = (registerNumhex.upper()).encode('UTF-8')

                if model == 'DD':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                elif model == 'SD':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                elif model == 'HD':  # HD寄存器对应modbus地址十进制41088~47231，十六进制A080~B87F
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num + 41088)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                else:
                    print("输入有误")
                    pass

                messageList = salveNum + order + address + registerNumhex
                messageStr = str(messageList, encoding="utf-8")
                crc16str = self.crc16Add(messageStr)
                crc16 = crc16str.encode('UTF-8')

                CMD1 = 0x01060064000109D5  # 报文示例，D100写入K1

                CMD = int.to_bytes(int(salveNum, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(order, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(address, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(registerNumhex, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(crc16, base=16), 2, byteorder='big')
                self.ser.write(CMD)

                # data_size = registerNum * 2
                # buffer_size = 5 + data_size
                buffer = self.ser.read(8)  # 一次只能写一个寄存器，所以固定为8位
                if buffer != '':
                    bufferHex = buffer.hex()
                    Flag = True
                else:
                    print("写入失败")
                    return False

        return Flag


plc_state = PLCState()
xj_rtu = modbus_RTU_communication()

if __name__ == '__main__':
    p = xj_rtu
    ser = p.ser
    if ser != False:
        # 从数据寄存器D100开始读取，读取3个寄存器的值（16位整数格式）
        t1 = time.time()
        dataRead = [['D0', 100]]
        while 1:
            resultRead = p.read_register(dataRead)
            time.sleep(1)
            print(resultRead)
        t2 = time.time()
        print(t2 - t1)
        print(resultRead)

        # 向数据寄存器D100开始3个寄存器，写入值（16位整数格式）
        dataWrite = [['SD100', 1], ['HD101', 2], ['SD102', 3]]
        p.write_register(dataWrite)

        ser.close()
