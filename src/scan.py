#!/usr/bin/python
# -*- coding: utf-8 -*-
from bluepy.btle import Scanner, DefaultDelegate
from subprocess import Popen
import time
import threading
import sys
import multiprocessing
from connect import BLEConnectHandler
from MQTT_ClientCommunicationHanlder import MQTT_Worker_Task


def Printer(string):
    print ('[SCANNER LOG]: ' + string)

class MyDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self,dev,isNewDev,isNewData,):
        if isNewDev:
            #Printer('Discovered device ' + str(dev.addr))
            isNewDev = isNewDev
        elif isNewData:
            #Printer('Received new data from ' + str(dev.addr))
            isNewData = isNewData

devicesMac = []

# Client Records will be maintained in this global Variable (See the example inside the Interface Specification document for full description)
Clients_Records = {
                    'BLEDeviceThreads': {'Thread_Count': 0, 'Thread_Info': {}},
                    'NewMQTTDeviceQueue': multiprocessing.Queue(),
                    'MQTTRegisteredDevices': {},
                    'GlobalMQTTSubsribedTopics':{},
                   }

# Start MQTT Client Thread for MQTT data handling and management
MQTTHandlerThread = threading.Thread(target=MQTT_Worker_Task, args=(Clients_Records, ))
MQTTHandlerThread.start()
# MQTTHandlerThread.join()

Printer('Start BLE scan')
scanner = Scanner().withDelegate(MyDelegate())

while True:
    # print("[ScanProcess] main Loop\n")
    # Start BLE scan and identify devices to be added
    #Printer('Start BLE scan')
    #scanner = Scanner().withDelegate(MyDelegate())
    devices = scanner.scan(5.0, passive=True)
    #Printer('BLE Scan complete')
    for dev in devices:
        if dev.addr not in devicesMac:
            #print ('[SCANNER LOG]:  Device %s (%s), RSSI=%d dB' % (dev.addr,dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
                #print ('[SCANNER LOG]:  %s = %s' % (desc, value))
                if value == 'b1301400-a7bd-46c7-8da4-d187c5058d0d':
                    devicesMac.append(dev.addr)
                    numberOfDevices = len(devicesMac)
                    Printer('Ble Client to Add:' + str(dev.addr))
                    Printer('Number of Clients:' + str(numberOfDevices))

                    for mac in devicesMac:
                        if mac not in Clients_Records['BLEDeviceThreads']['Thread_Info']:
                            # Create Thread to handle BLE device
                            Clients_Records['BLEDeviceThreads']['Thread_Count'] += 1
                            Clients_Records['BLEDeviceThreads']['Thread_Info'][mac] = {'Thread_Handler': 0, 'isTaskRunning': 1}
                            Clients_Records['BLEDeviceThreads']['Thread_Info'][mac]['Thread_Handler'] = threading.Thread(target=BLEConnectHandler,args=(Clients_Records, mac))
                            Clients_Records['BLEDeviceThreads']['Thread_Info'][mac]['Thread_Handler'].start()

    for mac in devicesMac:
        try:
            if Clients_Records['BLEDeviceThreads']['Thread_Info'][mac]['isTaskRunning'] == 0:
                del Clients_Records['BLEDeviceThreads']['Thread_Info'][mac]
                Clients_Records['BLEDeviceThreads']['Thread_Count'] -= 1
                devicesMac.remove(mac)
                Printer('MAC Array Updated: '+str(devicesMac))
                break #Only remove one device per iteration due to dynamic size operation
        except:
            Printer("Skip Iteration")

    time.sleep(10.0)