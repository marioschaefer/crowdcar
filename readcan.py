#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import can
from threading import Thread


canif = "can0"
canbps = 1000000
bus = None

# ip link set can0 up type can bitrate 100000
# ip link set can0 down

canid = {
    "ENGINE_COOLANT_TEMP": 0x05,
    "ENGINE_RPM": 0x0C,
    "VEHICLE_SPEED": 0x0D,
    "MAF_SENSOR": 0x10,
    "O2_VOLTAGE": 0x14,
    "THROTTLE": 0x11,
    "PID_REQUEST": 0x7DF,
    "PID_REPLY": 0x7E8
}


print('Bring up CAN0....')
os.system("/sbin/ip link set " + str(canif) + " up type can bitrate " + str(canbps))
time.sleep(1)
print('Ready')


try:
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()

    def can_rx_task():
        while True:
            message = bus.recv()
            if message.arbitration_id == canid['PID_REPLY'] and message.data[2] == canid['ENGINE_COOLANT_TEMP']:
                c = '{0:f} {1:x} {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
                s = ''
                for i in range(message.dlc):
                    s += '{0:x} '.format(message.data[i])
                temperature = message.data[3] - 40  # Convert data into temperature in degree C
                print('\r {}  Coolant temp = {} degree C  '.format(c + s, temperature))

    t = Thread(target = can_rx_task)
    t.start()

    while True:
        # Sent a engine coolant temperature request
        msg = can.Message(arbitration_id=canid['PID_REQUEST'], data=[0x02, 0x01, canid['ENGINE_COOLANT_TEMP'],
                                                                     0x00, 0x00, 0x00, 0x00, 0x00], extended_id=False)
        bus.send(msg)
        time.sleep(0.1)


except KeyboardInterrupt:
    os.system("/sbin/ip link set " + str(canif) + " down")
    print('Keyboard interrupt')
