import os, sys
from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *




def getTemp(ch1, ch2):
    temp1 = ch1.get_currentValue()
    temp2 = ch2.get_currentValue()
    print('channel 1/2: ' + '%2.1f / ' % temp1 + \
          '%2.1f' % temp2 + ' deg C')


def getDeviceInfo(m):
    upTime = str(m.get_upTime() / 1000)
    usbCurrent = str(m.get_usbCurrent())
    logs = m.get_lastLogs()
    print('device up time: ' + upTime + ' sec')
    print('device usb current: ' + usbCurrent + ' mA\n')
#    print('device logs:\n' + logs)
        
    


# virtual hub init
errmsg = YRefParam()

if YAPI.RegisterHub('127.0.0.1', errmsg) != YAPI.SUCCESS:
   sys.exit('init error')
   
   
# get sensor
sensor = YTemperature.FirstTemperature()

if sensor is None:
    sys.exit('no sensor connected')

if not (sensor.isOnline()):
    sys.exit('no device connected')
    

# get module
module = sensor.get_module()

if module is None:
    sys.exit('no module connected')

module.set_beacon(YModule.BEACON_OFF)
YAPI.Sleep(2000)
module.set_beacon(YModule.BEACON_ON)
YAPI.Sleep(3000)
module.set_beacon(YModule.BEACON_OFF)


# get device settings
serial = module.get_serialNumber()
name = module.get_logicalName()
luminosity = str(module.get_luminosity())

print('device serial: ' + serial)
print('device name: ' + name)
print('device luminocity: ' + luminosity + '%\n')


# get channels
channel1 = YTemperature.FindTemperature(serial + '.temperature1')
channel2 = YTemperature.FindTemperature(serial + '.temperature2')


# get temperature
while channel1.isOnline():
    if module.get_beacon() == YModule.BEACON_ON:
        getTemp(channel1, channel2)
        getDeviceInfo(module)
        YAPI.Sleep(1000)
    YAPI.Sleep(500)

YAPI.FreeAPI()