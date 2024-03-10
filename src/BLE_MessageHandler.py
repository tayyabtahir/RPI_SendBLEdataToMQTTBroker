import random
import time
import multiprocessing
import threading
import sys
import numpy as np
import binascii
from ParameterList import ParameterListD
import struct


def BLE_MessageHandler(MQTT_Client_Record, macAddr, Operation, ReceivedMessageFromBLEDevice):

	#Constant used for readability
	OPERATION_RECV_MESSAGE_FROM_BLE_DEV = 1
	OPERATION_SEND_MESSAGE_TO_BLE_DEV = 2

	#defines for Data Parameters
	COMMAND_SEND_DATA_TO_RPI = '@'
	COMMAND_SET_PARAMETER_MESSAGE = 'A'
	COMMAND_READ_PARAMETER_MESSAGE = 'Q'

	MESSAGE_START_BYTE_INDEX = 0
	MESSAGE_2ND_START_BYTE_INDEX = 1
	MESSAGE_TYPE_INDEX = 2
	MESSAGE_PARAMETER_TYPE_INDEX = 3
	MESSAGE_LENGTH_HIGH_BYTE_INDEX = 4
	MESSAGE_LENGTH_LOW_BYTE_INDEX = 5
	MESSAGE_TOPIC_INDEX = 6
	MESSAGE_PARAMETER_VALUE_START_INDEX = 7



	def Printer(string):
		print("[BLE MSG HANDLER LOGS][" + str(macAddr) + "]: " + string)


	def CalcCRCByte(InputString):
		
		CalcCRC = 0

		for element in InputString:
			#print("CalcCRC: ",CalcCRC, " ::: element: ",int(element))
			try:
				CalcCRC = CalcCRC + int(element)
			except:
				CalcCRC = CalcCRC + ord(element)

			CalcCRC = CalcCRC & 0xFF	# Treat like a byte (as crc is 1 byte wide)

		return CalcCRC


	def VerifyCRC(CalcCRC, InputString):

		isCRCCorrect = 0

		if CalcCRC == InputString[len(InputString)-3]:
			isCRCCorrect = 1
		else:
			Printer("[ERROR] Incorrect CRC Received")

		#Printer("Received CRC: "+ str(InputString[len(InputString)-3]) + "\tCalculated CRC: " + str(CalcCRC))

		return isCRCCorrect


	def ReadInstrumentDataMessage(InputString):

		MessageType = 0
		ReadParamIDX = 0
		ReadParamLen = 0
		ReadPublishTopic = 0
		ReadParamVal = 0
		ReadParamRefKey = 0

		#if InputString[0] == '$' and InputString[1] == '$' and \
			#InputString[len(InputString)-2] == '#' and InputString[len(InputString)-1] == '#':

		MessageType = InputString[MESSAGE_TYPE_INDEX] #InputString[2]
		ReadParamIDX = InputString[MESSAGE_PARAMETER_TYPE_INDEX] #InputString[3]

		ReadParamLen = InputString[MESSAGE_LENGTH_HIGH_BYTE_INDEX]
		ReadParamLen = ((ReadParamLen<<8) & 0xFF00) | (InputString[MESSAGE_LENGTH_LOW_BYTE_INDEX] & 0x00FF)

		#Dummy code for uneven messages received
		DummyReadParamLen = len(InputString[7:len(InputString)-3])
		if DummyReadParamLen > ReadParamLen:
			Printer("Length Mismatch: " + str(ReadParamLen) + "->" + str(DummyReadParamLen))
			#Printer("Length Mismatch in Bytes: " + str(InputString.length))
			
			ReadParamLen = DummyReadParamLen

		ReadPublishTopic = InputString[MESSAGE_TOPIC_INDEX] #InputString[5]
		#ReadParamVal = InputString[6:6+ReadParamLen].decode("ascii")

		#ReadParamVal = "".join([str(element) for element in InputString[6:6+ReadParamLen]])
		#for elem in InputString[6:6+ReadParamLen]:
			#ReadParamVal = ReadParamVal + str(elem)

		for Param in ParameterListD:
			if ParameterListD[Param]['IDX'] == ReadParamIDX:
				ReadParamRefKey = ParameterListD[Param]
				#Printer("Identified Parameter From ParameterList: " + str(Param))
				break

		# parameter value extraction based upon type		
						
		if ReadParamRefKey['DataType'] == "Char":
			ReadParamVal = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX] & 0xFF

		elif ReadParamRefKey['DataType'] == "Int":
			strFloat = b''
			strFloat = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX : MESSAGE_PARAMETER_VALUE_START_INDEX + ReadParamLen]
			ReadParamVal = 0
			counter = 0
			for element in strFloat:
			    ReadParamVal = (ReadParamVal) | (element << counter)
			    counter +=8 #shift 8 bits and patch next byte

		elif ReadParamRefKey['DataType'] == "Float":
			strFloat = b''
			strFloat = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX : MESSAGE_PARAMETER_VALUE_START_INDEX + ReadParamLen]
			ReadParamVal = struct.unpack('f', strFloat)[0]
			ReadParamVal = float("{:.4f}".format(ReadParamVal))

		elif ReadParamRefKey['DataType'] == "Double":
			strFloat = b''
			strFloat = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX : MESSAGE_PARAMETER_VALUE_START_INDEX + ReadParamLen]
			ReadParamVal = struct.unpack('d', strFloat)[0]
			ReadParamVal = float("{:.4f}".format(ReadParamVal))


		else: # 'String' and everything else
			try:
	  			ReadParamVal = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX : MESSAGE_PARAMETER_VALUE_START_INDEX + ReadParamLen].decode("ascii")
			except:
	  			Printer("UTF-8 Decoding Failed trying String Operation")
	  			ReadParamVal = InputString[MESSAGE_PARAMETER_VALUE_START_INDEX : MESSAGE_PARAMETER_VALUE_START_INDEX + ReadParamLen].decode('unicode-escape')
		

		#print(MessageType, "----", ReadParamIDX, "----", ReadParamLen, "----", ReadPublishTopic, "----",ReadParamVal, "----" ,ReadParamRefKey)

		return 	MessageType, ReadParamIDX, ReadParamLen, ReadPublishTopic, ReadParamVal, ReadParamRefKey


	def MakeSetParameterCommandForEndNode(ParameterDict):

		OutputString = b''

		ParamIDX = ParameterDict['IDX']

		if ParameterDict['DataType'] == 'Char':
			ParamLen = 1
			ParamVal = ParameterDict['Value']

		elif ParameterDict['DataType'] == 'Int':
			ParamLen = 4
			ParamVal = ParameterDict['Value']

		elif ParameterDict['DataType'] == 'Float':
			ParamLen = 4
			ParamVal = ParameterDict['Value']

		elif ParameterDict['DataType'] == 'Double':
			ParamLen = 8
			ParamVal = ParameterDict['Value']

		elif ParameterDict['DataType'] == 'Boolean':
			ParamLen = 1
			if ParameterDict['Value'] == True:
				ParamVal = '1'
			else:
				ParamVal = '0'

		elif ParameterDict['DataType'] == 'String':
			ParamLen = len(ParameterDict['Value'])
			ParamVal = ParameterDict['Value']
		
		CRCByte = CalcCRCByte(str(ParamIDX) + str(ParamLen) + str(ParamVal))

		#Printer("Set Param Command" + str(ParamIDX) + str(ParamLen) + str(ParamVal) + str(CRCByte))

		#OutputList = ['$', '$', 0x41, ParamIDX, ((ParamLen>>8) & 0xFF), (ParamLen & 0xFF), ParamVal, CRCByte, '#', '#']
		#OutputString =  bytearray(OutputList)

		if ParameterDict['DataType'] == 'String':
			OutputString = str("$;$;" + str(COMMAND_SET_PARAMETER_MESSAGE) + ";" +  str(ParamIDX) + ";" + str(ParamLen) + ";" + str(ParamVal) + ";" + str(CRCByte) + ";#;#")
		else:
			OutputString = str("$;$;" + str(COMMAND_SET_PARAMETER_MESSAGE) + ";" +  str(ParamIDX) + ";" + str((ParamLen>>8) & 0xFF) + str(ParamLen & 0xFF) + ";" + str(ParamVal) + ";" + str(CRCByte) + ";#;#")
		
		#print("***********************************************************************************************************************")
		#Printer("[Set Parameter]: " + str(OutputString))
		#print("***********************************************************************************************************************")
		#OutputString = "$$" + 0x41 + (ParamIDX & 0xFFFF) + ParamLen + ParamVal + CRCByte + "##"

		return OutputString


	def MakeReadParameterStringForEndNode(ParameterDict):
		ParamIDX = ParameterDict['IDX']
		CRCByte = ParamIDX

		OutputString = str("$;$;" + str(COMMAND_READ_PARAMETER_MESSAGE) + ";" + str(ParamIDX) + ";" + str(CRCByte) + ";#;#")
		
		#print("***********************************************************************************************************************")
		#Printer("[Read Parameter]: " + str(OutputString))
		#print("***********************************************************************************************************************")

		return OutputString


	def EnqueNewDeviceForMQTTRegisteration(ReadParamRefKey, ReadParamVal):

		if ('MetaDevicesInfo' in MQTT_Client_Record):
			if (macAddr in MQTT_Client_Record['MetaDevicesInfo']):
				MQTT_Client_Record['MetaDevicesInfo'][macAddr][ReadParamRefKey['Identity']] = ReadParamVal

				if ('MQTT_Client_ID' in MQTT_Client_Record['MetaDevicesInfo'][macAddr].keys()) and \
					('MQTT_Client_Username' in MQTT_Client_Record['MetaDevicesInfo'][macAddr].keys()):

					New_MQTT_Client = {
					'Mac_Address' : macAddr,
					'ClientID' : MQTT_Client_Record['MetaDevicesInfo'][macAddr]['MQTT_Client_ID'],
					'Client_UserName' : MQTT_Client_Record['MetaDevicesInfo'][macAddr]['MQTT_Client_Username'],
					'Client_Pass' : "",
					}

					# Populate as new client
					MQTT_Client_Record['NewMQTTDeviceQueue'].put(New_MQTT_Client)
					Printer ("Register new Client: " + str(New_MQTT_Client['ClientID']))

					#delete record as not needed anymore
					del MQTT_Client_Record['MetaDevicesInfo'][macAddr]

			else:
				DictNewParam = {ReadParamRefKey['Identity'] : ReadParamVal}
				MQTT_Client_Record['MetaDevicesInfo'] = {macAddr : DictNewParam}

		else:
			DictNewParam = { ReadParamRefKey['Identity'] : ReadParamVal}
			MQTT_Client_Record['MetaDevicesInfo'] = {macAddr : DictNewParam}

			#time.sleep(10)



	def EnqueMessageForCloud(ReadParamRefKey, ReadParamVal, ReadPublishTopic):

		for Param in ParameterListD:
			if ParameterListD[Param]['IDX'] == ReadPublishTopic:
				#if publish topic has not been set initially, populate with default topic then 
				if ~('Value' in ParameterListD[Param].keys()):
					ParameterListD[Param]['Value'] = ParameterListD[Param]['Identity']
				MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToPublish'] = ParameterListD[Param]['Value']
				break

		#if ~(macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys()):
			#Printer("[Error] **** Unable to Enque Cloud Message, Client not created Yet!!!")

		if macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys():

				#if Extreme Data send without making a JSON
				# Special Handling for these data
				# JSON strings are already sent from NRF so don't make one and send data as it is
				# e.g Extreme_Data->'IDX': 71 see ParameterList.py
				if ReadParamRefKey['IDX'] == 71:
					#message = str(ReadParamVal)
					MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue_Ext'].put(ReadParamVal, block=True)
					Printer("ExtData: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue_Ext'].qsize()))
					#Printer("Publish Queue Count: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue'].qsize()))
				else:
					#message = "{\"xRMS\":" + str(message_count) + "}"
					message = "{\"" + ReadParamRefKey['Identity'] + "\":" + str(ReadParamVal) + "}"
					MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue'].put(message)
					Printer("CloudData: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue'].qsize()))
					#Printer("Publish Queue Count: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Publish_Queue'].qsize()))

		else:
			Printer("[ERROR][CLOUD MSG]: MQTT Client " + str(macAddr) + " not registered on MQTT")


	def EnqueMessageForSubscribeToTopic(ReadParamRefKey, ReadParamVal):

		if macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys():
			topic = ReadParamVal

			if 'TopicToSubscribe' in MQTT_Client_Record['MQTTRegisteredDevices'][macAddr].keys():
				MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToSubscribe']['TopicToSubscribeQueue'].put(topic)

			else:

				MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToSubscribe'] = {'SubscribedTopics': [], 'TopicToSubscribeQueue': multiprocessing.Queue()}
				MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToSubscribe']['TopicToSubscribeQueue'].put(topic)
				

			#Printer("Subscribe Queue Count: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Subscribe_Queue'].qsize()))
			#Printer("ReadParamRefKey: " + str(ReadParamRefKey))
			Printer("Subscribe to New Topic: " + str(topic))

			
			for elem in ParameterListD:
				if ParameterListD[elem]['IDX'] == ReadParamRefKey['IDX']:
					ParameterListD[elem]['IDX'] = ReadParamRefKey['Identity']
					ParameterListD[elem]['IDX'] = ReadParamRefKey['Identity']
					break
		else:
			Printer("[ERROR][SUBSCRIBE MSG]: MQTT Client " + str(macAddr) + " not registered on MQTT")


	def SavePublishingTopic(ReadParamRefKey, ReadParamVal):

		if macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys():
			topic = ReadParamVal
			MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToPublish'] = ReadParamVal
			Printer("Published Topic Updated: " + str (MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['TopicToPublish']) + "For MAC Address: " + str(macAddr))

		else:
			Printer("[ERROR]: MQTT Client " + str(macAddr) + " not registered on MQTT")


	def ProcessCloudMessage():

		TopicReceivedFrom = 0
		ReceivedMessageContent = 0
		ParameterToSet = 0
		ParameterValueToSet = 0
		ParameterToRead = 0
		ParameterDict = {'IDX': 0, 'Value': ''}
		OutputString = ''

		if 'MQTTRegisteredDevices' in MQTT_Client_Record.keys():
			if macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys():

				if MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Subscribe_Queue'].qsize():
					
					#message = str(MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Subscribe_Queue'].get())
					ParameterDict = MQTT_Client_Record['MQTTRegisteredDevices'][macAddr]['Subscribe_Queue'].get()

					#print(ParameterDict)
					#Printer("[ERROR]: Add Support For Cloud Message Processing")

					if ParameterDict['ToSet'] == 1:
						#Printer("Make Set Parameter Message")
						OutputString = MakeSetParameterCommandForEndNode(ParameterDict)
						Printer("Make Set Parameter Message: " + str(OutputString))
					elif ParameterDict['ToSet'] == 0:
						#Printer("Make Read Parameter Message")
						OutputString = MakeReadParameterStringForEndNode(ParameterDict)
						Printer("Make Read Parameter Message: " + str(OutputString))


		else:
			Printer("[ERROR]: MQTT Client " + str(macAddr) + " not registered on MQTT")


		return OutputString



	def BLEIncomingMessageHandler(InputString):
		#Printer("BLEIncomingMessageHandler(): " + str([InputString[0:5]]) + "...")
		Printer("BLEIncomingMessageHandler()")

		MessageType = 0
		ReadParamIDX = 0
		ReadParamLen = 0
		ReadPublishTopic = 0
		ReadParamVal = 0
		ReadParamRefKey = 0

		#for elem in InputString:
			#print(elem)

		if VerifyCRC(CalcCRCByte(InputString[3: len(InputString)-3]), InputString):

			MessageType, ReadParamIDX, ReadParamLen, ReadPublishTopic, ReadParamVal, ReadParamRefKey = ReadInstrumentDataMessage(InputString)

			#Printer("Instrument Data Received: " + str(ReadParamRefKey))

			# Parameter for MQTT Client Registeration
			#if ReadParamRefKey['IDX'] >= 200 and ReadParamRefKey['IDX'] <= 202:
			if ReadParamRefKey['IDX'] in range(200, 202):
				EnqueNewDeviceForMQTTRegisteration(ReadParamRefKey, ReadParamVal)

			elif ('MQTTRegisteredDevices' in MQTT_Client_Record):
				if (macAddr in MQTT_Client_Record['MQTTRegisteredDevices'].keys()):

					#See "Last_Dev_Param" parameter for cloud parameter inside ParameterListD
					if ReadParamRefKey['IDX'] in range(1, 82):
						EnqueMessageForCloud(ReadParamRefKey, ReadParamVal, ReadPublishTopic)

					#-------------------------------------------------------------
					# Internal Data for Gateway-Node Dont send to Cloud
					#-------------------------------------------------------------
					#Printer("**Here: ReadParamRefKey['IDX']: " + str(ReadParamRefKey['IDX']))

					#Paramter for topic to subscribe to
					elif ReadParamRefKey['IDX'] in range(203, 208):
						EnqueMessageForSubscribeToTopic(ReadParamRefKey, ReadParamVal)

					#Paramter for updating Publisihing topic
					elif ReadParamRefKey['IDX'] in range(211, 220):
						SavePublishingTopic(ReadParamRefKey, ReadParamVal)

					else:
						Printer("[WARNING] Unhandled Parameter, Ignoring furthur action: " + str(ReadParamRefKey['IDX']))
				else:
					Printer("[ERROR] Unable to Enque Message, Client not created Yet!!!")

		else:
			Printer("[ERROR] Incorrect CRC Received")


	def BLEOutgoingMessageHandler():
		OutgoingCommand = ''

		OutgoingCommand = ProcessCloudMessage()

		if OutgoingCommand != '':
			Printer("BLEOutgoingMessageHandler(): ")

		return OutgoingCommand


	OutputString = ''
	
	# Handle Incoming messages from BLE node and take appropiriate actions
	if Operation == OPERATION_RECV_MESSAGE_FROM_BLE_DEV:
		#Printer("Start BLE Handling")
		BLEIncomingMessageHandler(ReceivedMessageFromBLEDevice)
		#Printer("Start BLE Handling")


	elif Operation == OPERATION_SEND_MESSAGE_TO_BLE_DEV:

		#def Ble_ClientHandler(MQTT_Client_Record, macAddr, Operation, ReceivedMessageFromBLEDevice):
		OutputString = BLEOutgoingMessageHandler()

	else:
		Printer("[ERROR]: Undefined Operation : " + str(Operation))


	return OutputString