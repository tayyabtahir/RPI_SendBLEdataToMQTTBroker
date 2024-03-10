ParameterListD = {

	'Firmware_Version' : {
		'IDX': 1,
		'Identity': "firmVersion",
		'DataType':	"Float", 
	},

	'Serial_Number' : {
		'IDX': 2,
		'Identity': "Serial_Number"
	},

	'Sensor_Status' : {
		'IDX': 3,
		'Identity': "Sensor_Status"
	},	

	'Restart_Node' : {
		'IDX': 4,
		'Identity': "reStart",
		'DataType':	"Boolean",
	},

	'Reset_Sensor' : {
		'IDX': 5,
		'Identity': "Reset_Sensor"
	},

	'Battery_Status' : {
		'IDX': 6,
		'Identity': "Battery_Status"
	},

	'Temperature' : {
		'IDX': 8,
		'Identity': "Temp",
		'DataType':	"Double" 
	},

	'Sleep_Wakeup_Cycle' : {
		'IDX': 9,
		'Identity': "Sleep_Wakeup_Cycle"
	},



#-------------------------------------------------------------
# Internal Data for Gateway-Node Dont send to Cloud
#-------------------------------------------------------------
	'MQTT_Client_ID' : {
		'IDX': 200,
		'Identity': "MQTT_Client_ID",
		'DataType':	"String" 
	},

	'MQTT_Client_Username' : {
		'IDX': 201,
		'Identity': "MQTT_Client_Username",
		'DataType':	"String" 
	},

	'MQTT_Client_Password' : {
		'IDX': 202,
		'Identity': "MQTT_Client_Password",
		'DataType':	"String" 
	},



	'MQTT_Client_Sub_Topic1' : {
		'IDX': 203,
		'Identity': "v1/devices/me/attributes",
		'DataType':	"String" 
	},

	'MQTT_Client_Sub_Topic2' : {
		'IDX': 204,
		'Identity': "v1/devices/me/rpc/request/+",
		'DataType':	"String" 
	},
	
	'MQTT_Client_Sub_Topic3' : {
		'IDX': 205,
		'Identity': "MQTT_Client_Sub_Topic3",
		'DataType':	"String" 
	},
		
	'MQTT_Client_Sub_Topic4' : {
		'IDX': 206,
		'Identity': "MQTT_Client_Sub_Topic4",
		'DataType':	"String" 
	},
		
	'MQTT_Client_Sub_Topic5' : {
		'IDX': 207,
		'Identity': "MQTT_Client_Sub_Topic5",
		'DataType':	"String" 
	},
		
	'MQTT_Client_Sub_Default' : {
		'IDX': 208,
		'Identity': "rpiGateway",
		'DataType':	"String" 
	},
		


	
	'MQTT_Client_Pub_Topic1' : {
		'IDX': 211,
		'Identity': "v1/devices/me/telemetry",
		'DataType':	"String" 
	},

	'MQTT_Client_Pub_Topic2' : {
		'IDX': 212,
		'Identity': "v1/devices/me/trendopeak",
		'DataType':	"String" 
	},

	'MQTT_Client_Pub_Topic3' : {
		'IDX': 213,
		'Identity': "v1/devices/me/attributes",
		'DataType':	"String" 
	},

	'MQTT_Client_Pub_Topic4' : {
		'IDX': 214,
		'Identity': "MQTT_Client_Pub_Topic4",
		'DataType':	"String" 
	},

	'MQTT_Client_Pub_Topic5' : {
		'IDX': 215,
		'Identity': "MQTT_Client_Pub_Topic5",
		'DataType':	"String" 
	},

	'MQTT_Client_Pub_Default' : {
		'IDX': 216,
		'Identity': "rpiGateway",
		'DataType':	"String" 
	},


	'MQTT_Client_Connected' : {
		'IDX': 220,
		'Identity': "MQTT_Client_Connected",
		'DataType':	"Char" 
	},
}