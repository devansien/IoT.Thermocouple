import os, sys
import boto3
from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *




TABLE_NAME = 'IoTThermocoupleData'
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''




# aws dynamo db i/o
def createTable(client):
    table = client.create_table(
        TableName = TABLE_NAME,
        KeySchema = [
            {
                'AttributeName': 'device-id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions = [
            {
                'AttributeName': 'device-id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput = {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    client.get_waiter('table_exists').wait(TableName = TABLE_NAME)
    print('table with name %s created.\n' % TABLE_NAME)


def putTemperature(client, id, temperature):
    response = client.put_item(
        TableName = TABLE_NAME,
        Item = {
            'device-id': { 'S': id },
            'temperature': { 'L': temperature }
        }
    )
    
    print('device with id %s and temperature %s saved.\n' % (id, temperature))




# thermocouple
def getTemp(ch1, ch2):
    temp1 = ch1.get_currentValue()
    temp2 = ch2.get_currentValue()
    putTemperature(dbClient, serial, temp1)
    print('channel 1/2: ' + '%2.1f / ' % temp1 + \
          '%2.1f' % temp2 + ' deg C')


def getDeviceInfo(m):
    upTime = str(m.get_upTime() / 1000)
    usbCurrent = str(m.get_usbCurrent())
    logs = m.get_lastLogs()
    print('device up time: ' + upTime + ' sec')
    print('device usb current: ' + usbCurrent + ' mA\n')
#    print('device logs:\n' + logs)
        
    


# dynamo db init
dbClient = boto3.client(
    'dynamodb',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY,
    region_name = "us-east-1"
)

createTable(dbClient)


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