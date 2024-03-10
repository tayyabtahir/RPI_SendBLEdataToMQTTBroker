import paho.mqtt.client as mqtt
import random
import time
import multiprocessing
import json
from ParameterList import ParameterListD as LocalParameterList

broker = 'broker.hivemq.com'
topic = "python/mqtt"
port = 1883

def Printer(string):
	print("[MQTT LOG]: " + string)
	#string = string

def DebugPrinter(string):
	print("[MQTT DEBUG LOG]: " + string)


def MQTT_Worker_Task(MQTT_Client_Record):

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(client, userdata, flags, rc):
		ClientToPublish = {}
		DataToPublish = {}
		#Printer ("on_connect():")

		'''
		MQTT Paho Connection Return Codes
		0: Connection successful
		1: Connection refused – incorrect protocol version
		2: Connection refused – invalid client identifier
		3: Connection refused – server unavailable
		4: Connection refused – bad username or password
		5: Connection refused – not authorised
		6-255: Currently unused.
		'''
		Printer("Connected with result code "+str(rc))

		for RegisteredDevice in MQTT_Client_Record['MQTTRegisteredDevices']:
			if client == MQTT_Client_Record['MQTTRegisteredDevices'][RegisteredDevice]['MQTT_Handle']:
				#ClientToPublish = MQTT_Client_Record['MQTTRegisteredDevices'][RegisteredDevice]
				DataToPublish['IDX'] = 220 	#See 'MQTT_Client_Connected' in ParameterList.py
				DataToPublish['Value'] = rc & 0xFF #Byte Only
				DataToPublish['DataType'] = 'Char'
				DataToPublish['ToSet'] = 1

				MQTT_Client_Record['MQTTRegisteredDevices'][RegisteredDevice]['Subscribe_Queue'].put(DataToPublish)

				Printer("Publish to client: " + str(RegisteredDevice))
				break;
		
		if not DataToPublish:
			print("**********************************************************************")
			print("Failed To Push Data : " + str(rc) + " On Client: " + str (client))
			print(client.client_id())
			print(userdata)
			print(flags)
			print(rc)
			print("**********************************************************************")


		#MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['Publish_Queue']

	def on_publish(mqttc, obj, mid):
		#Printer ("on_publish():")
		#Printer("mid: " + str(mid))
		Printer ("Publishing Message to Broker")

	# The callback for when a PUBLISH message is received from the server.
	def on_message(client, userdata, message):
		#get Message Payload		
		msg = str(message.payload.decode("utf-8"))
		Printer ("on_message():")
		#Printer("Received userdata: " + str(userdata))
		#Printer("Received message: " + str(msg))
		#Printer (client)
		#Printer (userdata)
		
		DataToPublish = {}

		for RegisteredDevice in MQTT_Client_Record['MQTTRegisteredDevices']:

			if client == MQTT_Client_Record['MQTTRegisteredDevices'][RegisteredDevice]['MQTT_Handle']:
				# parse JSON msg to dictionary
				JsonAsDict = json.loads(msg)
				for eachRecKey in JsonAsDict:
					isKeyFound = 0
					for Param in LocalParameterList:
						if LocalParameterList[Param]['Identity'] == eachRecKey:
							isKeyFound = 1
							DataToPublish['IDX'] = LocalParameterList[Param]['IDX']
							DataToPublish['Value'] = JsonAsDict[eachRecKey]
							DataToPublish['DataType'] = LocalParameterList[Param]['DataType']
							DataToPublish['ToSet'] = 1
							MQTT_Client_Record['MQTTRegisteredDevices'][RegisteredDevice]['Subscribe_Queue'].put(DataToPublish)
							Printer("Publish to client: " + str(RegisteredDevice))
							Printer("Data to Publish: " + str(DataToPublish))
							break
					if isKeyFound == 0:
						Printer("[ERROR]: Cant find Relevant key in ParameterList.py" + str(eachRecKey))
				break				
		

	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------

	def on_log(client, userdata, level, buf):
		#Will do something useful one day
		level = level
		#Printer ("on_log():")
		#Printer ("userdata : " + userdata)

	def on_subscribe(mqttc, obj, mid, granted_qos):
		#Printer ("on_subscribe():")
		#Printer("Subscribed: " + str(mid) + " " + str(granted_qos))
		Printer ("Subscribing Topic to Broker")

	def Initialise_clients(NewClient):

		#Add MQTT client if dont exist in record
		if (NewClient['Mac_Address'] in MQTT_Client_Record['MQTTRegisteredDevices'].keys()):
			Printer("Client Already exsist")

		else:

		    #callback assignment
		    client = mqtt.Client(NewClient['ClientID'],True) #don't use clean session

		    client.on_connect = on_connect        #attach function to callback
		    client.on_message = on_message        #attach function to callback
		    client.on_publish = on_publish
		    
		    client.on_subscribe = on_subscribe
		    client.username_pw_set(NewClient['Client_UserName'], NewClient['Client_Pass'])
		    client.on_log = on_log
		    client.enable_logger()

		    #connect and subscribe to default topic
		    client.connect(broker, port)
		    #client.subscribe(topic)

			# flags set
		    # client.topic_ack=[]
		    # client.run_flag=False
		    # client.running_loop=False
		    # client.subscribe_flag=False
		    # client.bad_connection_flag=False
		    # client.connected_flag=False
		    # client.disconnect_flag=False

		    MQTT_Client_Record['MQTTRegisteredDevices'][NewClient['Mac_Address']] = {
		    																		'ClientName' : NewClient['ClientID'],
																				    'MQTT_Handle': client,
																				    'Publish_Queue': multiprocessing.Queue(maxsize=0), 
																				    'Publish_Queue_Ext': multiprocessing.Queue(maxsize=0), 
																				    'Subscribe_Queue': multiprocessing.Queue(maxsize=0),
																				    'TopicToPublish' : "v1/devices/me/telemetry",
																				    'TopicToSubscribe' : {
																											'SubscribedTopics' : [],
																											'TopicToSubscribeQueue' : multiprocessing.Queue(),
																										}
																					}

	     	#add mqtt client  element to global dictionary
		    #Printer("Initializing Client :" + str(MQTT_Client_Record['MQTTRegisteredDevices'][NewClient['Mac_Address']]))
		    #Create Global Subscribed Topic list
		    if (NewClient['Mac_Address'] not in MQTT_Client_Record['GlobalMQTTSubsribedTopics'].keys()):
		    	MQTT_Client_Record['GlobalMQTTSubsribedTopics'][NewClient['Mac_Address']] = []
		    else:
		    	if (len(MQTT_Client_Record['GlobalMQTTSubsribedTopics'][NewClient['Mac_Address']]) > 0):
		    		for TopicToSubscribe in MQTT_Client_Record['GlobalMQTTSubsribedTopics'][NewClient['Mac_Address']]:
		    			#Printer("Subscribe from Global List" + str(TopicToSubscribe))
		    			client.subscribe(TopicToSubscribe)
		    
	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------

	Printer ("Start MQTT_Client.py")

	while 1:
		if 'NewMQTTDeviceQueue' in MQTT_Client_Record.keys():
			while MQTT_Client_Record['NewMQTTDeviceQueue'].qsize():
				clientInstance = MQTT_Client_Record['NewMQTTDeviceQueue'].get()
				if ~(clientInstance['Mac_Address'] in MQTT_Client_Record['MQTTRegisteredDevices'].keys()):
					Printer("Initializing Client :" + str(clientInstance))
					Initialise_clients(clientInstance)


		if 'MQTTRegisteredDevices' in MQTT_Client_Record.keys():
			#runtime values might change so keep that check
			if MQTT_Client_Record['MQTTRegisteredDevices'] != '':

				try:
					# MQTT Client Record isnt empty
					for MQTT_Client in MQTT_Client_Record['MQTTRegisteredDevices'] :

						#Publish all the pending messages for the client
						while MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['Publish_Queue'].qsize():

							message = str(MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['Publish_Queue'].get())
							Printer("Cloud Content:: " + message)
							result = MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['MQTT_Handle'].publish(MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToPublish'], message)

						#Publish all the pending Extreme Data messages for the client
						while MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['Publish_Queue_Ext'].qsize():
							message = str(MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['Publish_Queue_Ext'].get())
							Printer("ExtData Content:: " + message)
							Printer("[WARNING] Please Uncomment Extreme Data Publishing " + str(result))
							#result = MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['MQTT_Handle'].publish(MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToPublish'], message)
							#Printer("MQTTT Publish Returned: " + str(result))

						
						#Subscribe the topic if needed by the node
						while MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToSubscribe']['TopicToSubscribeQueue'].qsize():

							TopicToSubscribe = str(MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToSubscribe']['TopicToSubscribeQueue'].get())

							if TopicToSubscribe not in MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToSubscribe']['SubscribedTopics']:
								MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['MQTT_Handle'].subscribe(TopicToSubscribe)
								MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['TopicToSubscribe']['SubscribedTopics'].append(TopicToSubscribe)

								#if topic is not in global array add there as well
								if (TopicToSubscribe not in MQTT_Client_Record['GlobalMQTTSubsribedTopics'][MQTT_Client]):
									MQTT_Client_Record['GlobalMQTTSubsribedTopics'][MQTT_Client].append(TopicToSubscribe)


						#Wait for any message from the subscribed topics
						MQTT_Client_Record['MQTTRegisteredDevices'][MQTT_Client]['MQTT_Handle'].loop(1)
				except:
					Printer("Skip Iteration")
		
		#Printer("MQTT Thread Running")			
		time.sleep(1)