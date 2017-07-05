#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import csv
from time import sleep

# set to True to disable import of w1thermsensor
devenv = True
filename = 'temps.csv'
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


print("Getting sensors")
sensors = []
file = None
try:
    for sensor in W1ThermSensor.get_available_sensors():
        print("Sensor %s found" % sensor.id)
        sensors.append(sensor.id)
except Exception as exc:
    print("Error while getting available sensors: %s" % exc)
    exit(99)

if len(sensors) < 1:
    print("no sensors found, exit")
    exit(97)

print("opening file for data saving")
try:
    file = CsvWriter(filename, sensors)
except Exception as exc:
    print("Error while opening file(%s) for writing: %s" % (filename, exc))
    exit(98)

print("file opened, start reading temps")
while True:
    tempreading = {}
    for sensorid in sensors:
        temp = 0
        try:
            temp = W1ThermSensor(sensor_id=sensorid).get_temperature()
        except Exception as exc:
            print("failed to get temp for Sensor(%f): %s" % (sensorid, exc))
        print("Sensor %s has temp %.2f" % (sensorid, temp))
        tempreading[sensorid] = temp

    try:
        file.writetempline(tempreading)
    except Exception as exc:
        print("failed to write temperatures to file: %s" % exc)
    sleep(15)
