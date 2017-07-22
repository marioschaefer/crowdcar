#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import csv
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO


# set to True to disable import of w1thermsensor
devenv = False
gpiowarningled = 24
gpiodisplchangebtn = 23
displaypage = 1
displaymaxpage = 3
maxtemp = 30
filename = datetime.now().strftime("%Y%m%d_%H%M%S_") + 'tempreadings.csv'
if not devenv:
    from w1thermsensor import W1ThermSensor


class CsvWriter:
    def __init__(self, filename, header):
        """
        :param filename: 
        :type filename: 
        :param header: 
        :type header: 
        """
        self.filename = filename
        self.header = header
        self.filepointer = None
        self.filepath = os.path.realpath(__file__)
        self._openfp()

    def _openfp(self):
        """
        :return: 
        :rtype: 
        """
        try:
            fp = open(os.path.join(os.path.dirname(__file__), self.filename), 'w+', newline='')
            self.filepointer = csv.DictWriter(fp, fieldnames=self.header, delimiter=';', quoting=csv.QUOTE_ALL,
                                              quotechar='"')
            self.filepointer.writeheader()
        except Exception as exc:
            raise exc

    def closefp(self):
        """
        
        :return: 
        :rtype: 
        """
        if self.filepointer:
            self.filepointer.close()

    def writetempline(self, line):
        """
        
        :param line: 
        :type line: 
        :return: 
        :rtype: 
        """
        if self.filepointer:
            try:
                self.filepointer.writerow(line)
            except Exception as exc:
                raise exc
        else:
            raise PermissionError('cant write to file, no filepointer')


# handle the button event
def buttonEventHandler(pin):
    global displaypage
    if displaypage < displaymaxpage:
        displaypage += 1
    else:
        displaypage = 1
    print("handling button(pin: %s) event, select displaypage: %s" % (pin, displaypage))


def ledon(pin):
    GPIO.output(pin, 1)


def ledoff(pin):
    GPIO.output(pin, 0)


def exitprog(excode):
    GPIO.output(gpiowarningled, False)
    GPIO.cleanup()
    exit(excode)


def main():
    print("setting up GPIO")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpiodisplchangebtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(gpiowarningled, GPIO.OUT)
    GPIO.add_event_detect(gpiodisplchangebtn, GPIO.RISING, callback=buttonEventHandler, bouncetime=200)
    # GPIO.add_event_callback(23, buttonEventHandler, 100)
    GPIO.output(gpiowarningled, GPIO.HIGH)
    sleep(1)
    GPIO.output(gpiowarningled, False)

    print("Getting sensors")
    sensors = ["readtime"]
    file = None
    try:
        for sensor in W1ThermSensor.get_available_sensors():
            print("Sensor %s found" % sensor.id)
            sensors.append(sensor.id)
    except Exception as exc:
        print("Error while getting available sensors: %s" % exc)
        exitprog(99)

    if len(sensors) <= 1:
        print("no sensors found, exit")
        exitprog(97)

    print("opening file for data saving")
    try:
        file = CsvWriter(filename, sensors)
    except Exception as exc:
        print("Error while opening file(%s) for writing: %s" % (filename, exc))
        exitprog(98)

    print("file opened, start reading temps")
    while True:
        tempreading = {}
        maxtempexceeded = False
        for sensorid in sensors:
            if sensorid == "readtime":
                tempreading['readtime'] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                continue
            temp = 0
            try:
                temp = W1ThermSensor(sensor_id=sensorid).get_temperature()
            except Exception as exc:
                print("failed to get temp for Sensor(%s): %s" % (sensorid, exc))

            # check if temp is over maxtemp and issue warning + set warningled to on
            if temp >= maxtemp:
                print("Sensor %s exceeding max temp(%s): %.2f" % (sensorid, maxtemp, temp))
                maxtempexceeded = True
                ledon(gpiowarningled)
            else:
                print("Sensor %s has temp: %.2f" % (sensorid, temp))
            tempreading[sensorid] = temp

        try:
            file.writetempline(tempreading)
        except Exception as exc:
            print("failed to write temperatures to file: %s" % exc)
        sleep(1)

        # if the temperature is not exceeded, turn of our warningled
        if not maxtempexceeded:
            ledoff(gpiowarningled)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("keyboard interrupt, exiting")
        exitprog(50)
