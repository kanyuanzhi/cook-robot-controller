#!/usr/bin/env python
# -*- coding:utf-8 -*-
from binascii import *
import crcmod  # crcmod为专门用于crc校验的库
import serial
import os
import socket
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


class modbus_TCP_communication():
    def __init__(self):
        conf = configparser.ConfigParser()
        if os.path.isfile("config.ini"):
            conf.read("config.ini")
            host = conf.get("modbus_TCP_settings", "IP")
            port = int(conf.get("modbus_TCP_settings", "port"))
        self.ser = socket.socket()
        host = '192.168.6.6'
        port = 502
        try:
            self.ser.connect((host, port))
        except Exception as e:
            print(e)

    def read_register(self, datas):
        '''
        一次读n个数据寄存器D，从00 08开始：站号；功能码03；寄存器首地址；寄存器个数
        读D1000、D1001：04 22 00 00 00 06 01 03 03 E8 00 02

        Returns:
        写入成功，返回True
        '''
        if len(datas) == 0:
            pass
        else:
            TransmissionIdentifier = b'0422'  # 传输标识符
            ProtocolIdentifier = b'0000'  # 协议标识符
            bytesLen = b'0006'  # 字节长度
            salveNum = b'01'  # 站号；0x表示十六进制的int型变量，\x表示十六进制的字符型变量
            # print('0x{:02X}'.format(int(salveNum)))
            order = b'03'  # 功能码，寄存器读
            result = []  # 读取的返回结果，以[[D0, value0], [D1, value1]...]给出

            for data in datas:
                resultSingle = []
                modle = data[0][0:2].upper()

                registerNum = int(data[1])  # 读取的寄存器个数
                registerNumhex = hex(registerNum)[2:].zfill(4)
                registerNumhex = (registerNumhex.upper()).encode('UTF-8')

                if modle == 'DS' or modle == 'DD':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                    if modle == 'DD':
                        registerNum = 2  # 读取的寄存器个数固定为2
                        registerNumhex = hex(registerNum)[2:].zfill(4)
                        registerNumhex = (registerNumhex.upper()).encode('UTF-8')

                elif modle == 'HD' or modle == 'HS':  # HD寄存器对应modbus地址十进制41088~47231，十六进制A080~B87F
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num + 41088)[2:].zfill(4)
                    address = (address.upper()).encode('UTF-8')
                    if modle == 'HD':
                        registerNum = 2  # 读取的寄存器个数固定为2
                        registerNumhex = hex(registerNum)[2:].zfill(4)
                        registerNumhex = (registerNumhex.upper()).encode('UTF-8')
                else:
                    print("输入有误")
                    return

                # cmd12 = ('0x{:02X}'.format(int(salveNum))).encode('UTF-8')#从'1'变成'\x01'
                CMD1 = 0x042200000006010300010002  # 报文示例，读D0开始两个字节
                # a = struct.pack(">B", int(salveNum, base=16))
                # a += struct.pack(">B", int(order, base=16))
                # a += struct.pack(">H", int(address, base=16))
                # a += struct.pack(">H", int(registerNumhex, base=16))
                # a += struct.pack(">H", int(crc16, base=16))
                # self.ser.write(a)
                CMD = int.to_bytes(int(TransmissionIdentifier, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(ProtocolIdentifier, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(bytesLen, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(salveNum, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(order, base=16), 1, byteorder='big')
                CMD += int.to_bytes(int(address, base=16), 2, byteorder='big')
                CMD += int.to_bytes(int(registerNumhex, base=16), 2, byteorder='big')
                self.ser.send(CMD)

                data_size = registerNum * 2
                buffer_size = 9 + data_size
                buffer = self.ser.recv(buffer_size)
                bufferHex = buffer.hex()
                # print(bufferHex)
                for i in range(registerNum):
                    registerValue = int(bufferHex[(18 + 4 * i):(18 + 4 * i + 4)], base=16)
                    resultSingle.append([modle + str(num + i), registerValue])  # data[0]
                    plc_state.set(modle + str(num + i), registerValue)
                result.append(resultSingle)
        return result

    def write_register(self, datas):
        '''
        单个数据寄存器D写(单字写)：站号；功能码06；寄存器地址；数据内容
        D2写入K5000：01 06 00 02 13 88 25 5C

        多个数据寄存器D写(双字写)：站号；功能码10；寄存器地址；寄存器个数；字节数；数据内容
        D0、D1分别写入1、2：01 10 00 00 00 02 04 00 01 00 02

        数据寄存器D地址：K0~20479，H0~4FFF
        掉电保持数据寄存器HD0~HD999地址：K41088~47231， HA080~B87F
        Returns:
        写入成功，返回True
        '''
        if len(datas) == 0:
            pass
        else:
            TransmissionIdentifier = b'0422'  # 传输标识符
            ProtocolIdentifier = b'0000'  # 协议标识符

            for data in datas:
                bytesLen = b'0006'  # 单字写时，有效报文字节长度
                salveNum = b'01'  # 站号；0x表示十六进制的int型变量，\x表示十六进制的字符型变量
                order = b'06'  # 单字写，功能码

                modle = data[0][0:2].upper()

                wValue = int(data[1])  # 需要写入的十进制数，默认为单字写
                wValuehex = hex(wValue)[2:].zfill(4)
                wValuehex = (wValuehex.upper()).encode('UTF-8')

                if modle == 'DD' or modle == 'DS':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                    if modle == 'DD':  # D寄存器对应modbus地址十进制0~20479，十六进制0~4FFF
                        wValuehex = hex(wValue)[2:].zfill(8)
                        wValueLow = (wValuehex[4:8].upper()).encode('UTF-8')
                        wValueHigh = (wValuehex[0:4].upper()).encode('UTF-8')
                        bytesLen = b'000B'  # 双字写，有效报文字节长度
                        order = b'10'  # 双字写，功能码
                        registerNum = b'0002'  # 写入的寄存器个数
                        dataBytesLen = b'04'  # 写入的数值字节数
                elif modle == 'HS' or modle == 'HD':  # HD寄存器对应modbus地址十进制41088~47231，十六进制A080~B87F
                    num = int(data[0][2:])  # 寄存器的十进制编号
                    address = hex(num + 41088)[2:].zfill(4)  # 将num转换为4位16进制表示
                    address = (address.upper()).encode('UTF-8')
                    if modle == 'HD':
                        wValuehex = hex(wValue)[2:].zfill(8)
                        wValueLow = (wValuehex[4:8].upper()).encode('UTF-8')
                        wValueHigh = (wValuehex[0:4].upper()).encode('UTF-8')
                        bytesLen = b'000B'  # 双字写，有效报文字节长度
                        order = b'10'  # 双字写，功能码
                        registerNum = b'0002'  # 写入的寄存器个数
                        dataBytesLen = b'04'  # 写入的数值字节数
                else:
                    print("输入有误")
                    pass

                if modle == 'DS' or modle == 'HS':
                    CMD1 = 0x042200000006010600020001  # 报文示例，D2写入K1

                    CMD = int.to_bytes(int(TransmissionIdentifier, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(ProtocolIdentifier, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(bytesLen, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(salveNum, base=16), 1, byteorder='big')
                    CMD += int.to_bytes(int(order, base=16), 1, byteorder='big')
                    CMD += int.to_bytes(int(address, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(wValuehex, base=16), 2, byteorder='big')

                    self.ser.send(CMD)
                    buffer = self.ser.recv(12)  # 单字写，返回报文12位
                    if buffer != '':
                        bufferHex = buffer.hex()
                    else:
                        print("写入失败")
                        return False

                elif modle == 'DD' or modle == 'HD':
                    CMD1 = 0x04220000000B0110000A00020486A00001  # 报文示例，D10写入双子K100000

                    CMD = int.to_bytes(int(TransmissionIdentifier, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(ProtocolIdentifier, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(bytesLen, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(salveNum, base=16), 1, byteorder='big')
                    CMD += int.to_bytes(int(order, base=16), 1, byteorder='big')
                    CMD += int.to_bytes(int(address, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(registerNum, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(dataBytesLen, base=16), 1, byteorder='big')
                    CMD += int.to_bytes(int(wValueLow, base=16), 2, byteorder='big')
                    CMD += int.to_bytes(int(wValueHigh, base=16), 2, byteorder='big')
                    # print(CMD)
                    self.ser.send(CMD)
                    buffer = self.ser.recv(12)  # 双字写，返回报文12位
                    if buffer != '':
                        bufferHex = buffer.hex()
                    else:
                        print("写入失败")
                        return False
            return True


plc_state = PLCState()
modbus_tcp = modbus_TCP_communication()

if __name__ == '__main__':
    p = modbus_tcp

    # 从数据寄存器D100开始读取，读取3个寄存器的值（16位整数格式）
    # t1 = time.time()
    # dataRead = [['DD10', 1], ['DS1', 10], ['HD0', 1]]  # 如果是DD或者HD，即双字时，寄存器位数只能为1
    # resultRead = p.read_register(dataRead)
    # print(resultRead)
    # t2 = time.time()
    # print(t2 - t1)
    # print(resultRead)

    # 向数据寄存器D100开始3个寄存器，写入值（16位整数格式）
    # dataWrite = [['DD20', 1], ['DD42', 3], ['HS124', 100]]
    dataWrite = [['DD20', 1]]
    p.write_register(dataWrite)
