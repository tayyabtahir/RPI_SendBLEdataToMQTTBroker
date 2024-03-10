from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, UUID
import sys
import time
import binascii

#############################################################################
#   Global Variables
#############################################################################
devicesMac = []
global dev
global LEDConfig


class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print ("Discovered device", dev.addr)
        elif isNewData:
            print ("Received new data from", dev.addr)

    def handleNotification(self, cHandle, data):
        print ("Notification received\n")
        val = SensorConfig.read()
        print ("Accelerometer sensor raw value", binascii.b2a_hex(val))




print("Start scan")
scanner = Scanner().withDelegate(MyDelegate())
devices = scanner.scan(10.0, passive=True)
print("scan complete")
for dev in devices:
    print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        print ("  %s = %s" % (desc, value))
        if value == "b1301400-a7bd-46c7-8da4-d187c5058d0d":
           devicesMac.append(dev.addr)

numberOfDevices = len(devicesMac)

#for devmac in range(0 ,numberOfDevices-1, 1):
print("Connecting to device: %s" % (devicesMac[0]))
dev = Peripheral(devicesMac[0], addrType=ADDR_TYPE_RANDOM)
dev.setDelegate( MyDelegate() )


print ("Services...")
for svc in dev.services:
     print (str(svc))


Sensor = UUID("b1301400-a7bd-46c7-8da4-d187c5058d0d")
lightService = dev.getServiceByUUID(Sensor)
for ch in lightService.getCharacteristics():
    print (str(ch))


uuidConfig = UUID("b1301401-a7bd-46c7-8da4-d187c5058d0d")
SensorConfig = lightService.getCharacteristics(uuidConfig)[0]

# Enable notifications
dev.writeCharacteristic(SensorConfig.valHandle+1, bytes("\x01\x00", encoding='utf8'))

# Turn On LED
#SensorConfig.write(bytes("\x01", encoding='utf8'))
#time.sleep(1.0) 
# turn off LED
#SensorConfig.write(bytes("\x00", encoding='utf8'))


while True:
    if dev.waitForNotifications(1.0):
        # handleNotification() was called
        #val = SensorConfig.read()
        #print ("Accelerometer sensor raw value", binascii.b2a_hex(val))
        continue

    print("Waiting...")



dev.disconnect()
#val = LEDConfig.read()