from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, UUID
import sys
import time
import binascii
from argparse import ArgumentParser
from BLE_MessageHandler import BLE_MessageHandler

#############################################################################
#   Global Variables
#############################################################################
#devicesMac = []
#global macAddr

def BLEConnectHandler(Clients_Records, macAddr):

    #Constant used for readability
    RECV_MESSAGE = 1 # OPERATION_RECV_MESSAGE_FROM_BLE_DEV
    SEND_MESSAGE = 2 # OPERATION_SEND_MESSAGE_TO_BLE_DEV

    CompleteMessage = b""
    
    class MyDelegate(DefaultDelegate):

        def __init__(self, gBuffer):
            DefaultDelegate.__init__(self)
            self.Buffer = gBuffer

        def handleNotification(self, cHandle, data):
            #print ("\nNotification received")
            #print ("[",macAddr,"] raw Data: ", data)

            ReadMessage = b""

            #if the whole message is received in 1 go
            if b"$$" in data and b"##" in data:
                ReadMessage = b""
                ReadMessage = data
            #if the whole message is received in more then 1 go
            elif b"$$" in data:
                self.Buffer = b""
                self.Buffer = data
            else:
                self.Buffer += data
                #self.Buffer.extend(data)
                
                if b"##" in data:
                    ReadMessage = b""
                    ReadMessage = self.Buffer
                    self.Buffer = b""
            
            if ReadMessage != b"":
                lMessageStartIndex = ReadMessage.index(b"$$")
                lMessageEndIndex = ReadMessage.index(b"##")+2
                FinalReadMessage = ReadMessage[lMessageStartIndex:lMessageEndIndex]
                #print("Complete BLE Message: ",FinalReadMessage)
                BLE_MessageHandler(Clients_Records, macAddr, RECV_MESSAGE, FinalReadMessage)
            data = 0



    def get_args():
        arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
        arg_parser.add_argument('mac_address', help="MAC address of device to connect")
        args = arg_parser.parse_args()
        return args


    #args = get_args()
    #macAddr = args.mac_address


    print("[CONNECT LOGS]: Connecting to device: %s" % (macAddr))
    dev = Peripheral(macAddr, addrType=ADDR_TYPE_RANDOM)
    dev.setDelegate( MyDelegate(CompleteMessage) )


    # Get Services by UUID
    Sensor = UUID("b1301400-a7bd-46c7-8da4-d187c5058d0d")
    lightService = dev.getServiceByUUID(Sensor)
    for ch in lightService.getCharacteristics():
        print ("[CONNECT LOGS]: ", str(ch))


    # Get Characteristics by UUID
    uuidConfig = UUID("b1301401-a7bd-46c7-8da4-d187c5058d0d")
    SensorConfig = lightService.getCharacteristics(uuidConfig)[0]

    # Enable notifications
    dev.writeCharacteristic(SensorConfig.valHandle+1, bytes("\x01\x00", encoding='utf8'))
    
    RetryBleConnectionAttempt = 0

    while True:
        ReadMessage = 0
        ResponseMessage = 0
        
        try:

            if dev.waitForNotifications(1.0):
                continue

            ResponseMessage = BLE_MessageHandler(Clients_Records, macAddr, SEND_MESSAGE, ReadMessage)
            if ResponseMessage != '':
                #print("[" + str(macAddr)+ "] OutgoingMessage to Sensor: " + ResponseMessage)
                #print("[" + str(macAddr)+ "] OutgoingMessage Length: " + str(len(ResponseMessage)))

                TotalMessageLength = len(ResponseMessage)
                if TotalMessageLength <= 19:
                    SensorConfig.write(bytes(ResponseMessage, encoding='utf8'))

                else:
                    startIndex = 0
                    endIndex = 18
                    while(TotalMessageLength > 0):

                        SendPartialMessage = ResponseMessage[startIndex: endIndex]
                        SensorConfig.write(bytes(SendPartialMessage, encoding='utf8'))
                        TotalMessageLength = TotalMessageLength - (endIndex-startIndex)                    
                        startIndex = endIndex                    
                        if TotalMessageLength > 18:
                            endIndex += 18
                        else:
                            endIndex += TotalMessageLength
                        time.sleep(1)

            #Reset Connection Attempt
            RetryBleConnectionAttempt = 0

        except:

            if RetryBleConnectionAttempt < 5:
                RetryBleConnectionAttempt += 1
                print("[CONNECT LOGS]: Retry Connecting to " + str(macAddr))
                time.sleep(1)

            else:
                print ("[CONNECT LOGS]: Disconnect BLE Device")
                dev.disconnect()
                time.sleep(1)
                
                print ("[CONNECT LOGS]: Waiting to Empty Publish_Queue for Dev: ", str(macAddr))
                while Clients_Records['MQTTRegisteredDevices'][macAddr]['Publish_Queue'].qsize():
                    time.sleep(1)


                #MQTT device Closure
                if (len(Clients_Records['MQTTRegisteredDevices'][macAddr]['TopicToSubscribe']['SubscribedTopics']) > 0):

                    for SubTopic in Clients_Records['MQTTRegisteredDevices'][macAddr]['TopicToSubscribe']['SubscribedTopics']:
                        Clients_Records['MQTTRegisteredDevices'][macAddr]['MQTT_Handle'].unsubscribe(SubTopic)
                        print("[CONNECT LOGS]: Unsubscibe Topic: ", SubTopic)

                Clients_Records['MQTTRegisteredDevices'][macAddr]['MQTT_Handle'].disconnect()
                print("[CONNECT LOGS]: Disconnect MQTT client: ", macAddr)

                #print("********************************************************************")
                #print(str(Clients_Records['MQTTRegisteredDevices']))
                #print("********************************************************************")

                print ("[CONNECT LOGS]: Removing Device from  Registered Device List: ", str(macAddr))
                #Remove from MQTT Lists
                del Clients_Records['MQTTRegisteredDevices'][macAddr]

                #Notify that the thread is inactive
                Clients_Records['BLEDeviceThreads']['Thread_Info'][macAddr]['isTaskRunning'] = 0
                #break free and the task will end
                break

    #dev.disconnect()