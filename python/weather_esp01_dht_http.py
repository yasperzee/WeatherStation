#!/usr/bin/ python3
#
    #***** weather_esp01_dht_http.py  Usage: python3 weather_esp01_dht_http.py *****
#
#       Technology demo using http. ESP-01 as web-server.
#       This script reads temperature and humidity from DHT-11 or DHT-22 sensor
#       connected to ESP-01 and updates valid values to google sheet.
#
#*******************************************************************************

#TODO:      * Add retry / failsafe in case ESP01-server/sheet not available when connecting
#TODO:      * Add retry / failsafe in case ESP01-server and/or sheet gets unavailable

"""------------------------------ Version history ------------------------------

    v1.2   yasperzee   4'19    Classes to separate modules

    v1.1    yasperzee   4'19    Comparing DHT11 <--> DHT22
                Write dht01(DHT11) and dht02(DHT22) to the same sheet named DHT-COMP
                Added failreading count to sheet when ERROR_VALUE read
                Added _DEBUG_ flag

    v1.0    yasperzee   4'19    Release 2: In synch with weather_esp01_dht_http.ino (version 1.0)
                Is NOT! compatible with 'weather_esp01_dht_http.ino version < 1.0'
                Filename changed.
                Get node and sensor info.
                Some support for DHT-22.
                Writes to selected/named sheet on spreadsheet, not to spreadsheet which is first sheet.

    v0.3    yasperzee   3'19    Cleaning for release

    v0.2    yasperzee   3'19    update
                * Manipulate sheet so that NEW value is written to top row
                    --> Show on meters latest measured temperature & humidity
                        move rows down by one, delete row MAX_ROW+1, write values to top row
                * if sensorValue == ERROR_VALUE, do NOT send ERROR_VALUE to sheet

    v0.1    yasperzee   3'19
                Modified for dht11 sensor

    v0.5    yasperzee   2'19
                Some robustnest added to handle sensor values
                Add new values to next empty row.
                Added table and some visualization to sheet

    v0.4    yasperzee   2'19
                Update sheets with values
                Add current date and time to sheet with values

    v0.3    yasperzee   2'19
                Initial suppport for send values to sheeet
                Connects to googlesheets and read some values

    v0.2    yasperzee   2'19
                Support for nodemcu_weather v0.3, update tagPres accordingly

    v0.1    yasperzee   2'19
                Read webpage with sensor values
                combatible with nodemcu_weather v0.2

-----------------------------------------------------------------------------"""
# Imports
from __future__ import print_function
import time

from configuration import *
from SensorDHT import Sensor_DHT
from GoogleSheetsHandler import Gredentials
from GoogleSheetsHandler import WriteToSheet

# # # # # # # # # # # # # # # # CONFIGURATIONS  # # # # # # # # # # # # # # # #

_DEBUG_ = True # --> DEBUG
#_DEBUG_ = False #--> RELEASE

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if _DEBUG_ == True:
    RETRY_INTERVAL = 10*1    # 5*1 = 5 second retry if sensor reading(s) == ERROR_VALUE
    UPDATE_INTERVAL= 15*1   # 38*1 = 38 second -> 96 records / ~1h
else: # Release
    RETRY_INTERVAL = 3*60 # 3*60 = 3min retry if sensor reading(s) == ERROR_VALUE
    UPDATE_INTERVAL= 15*60 # 15*60 = 15min -> 96 records / 24h

class SensorDHT11(Sensor_DHT):
    pass

class SensorDHT22(Sensor_DHT):
    pass

def main():
    once = False;
    failCount = 0;

    while 1:
        if once == False:
            #print('Run only once')
            # If token.pickle does not exists, create newone.
            istoken = Gredentials()
            istoken.getToken();
            creds = istoken.creds
            del istoken

            # Read Node1 and Sensor information
            ival = SensorDHT11(request_info_url_dht_01)
            ival.readInfo();
            info1  = ival.getInfo()
            print("Info1: " + info1)
            del ival

            # Read Node2 and Sensor information
            ival = SensorDHT22(request_info_url_dht_02)
            ival.readInfo();
            info2  = ival.getInfo()
            print("Info2: " + info2)
            del ival

            # Write info to sheet
            updateSheet = WriteToSheet(ERROR_VALUE, ERROR_VALUE, ERROR_VALUE, ERROR_VALUE, 0)
            updateSheet.writeInfoToSheet(creds, info1, info2);
            del updateSheet
            once = True

        # Read current Temperature & Barometer values
        sval1 = SensorDHT11(request_values_url_dht_01)
        sval1.readSensors();
        temp_dht11  = sval1.getTemp()
        humid_dht11 = sval1.getHumid()
        del sval1

        sval2 = SensorDHT22(request_values_url_dht_02)
        sval2.readSensors();
        temp_dht22  = sval2.getTemp()
        humid_dht22 = sval2.getHumid()
        del sval2

        # Append values to spreadsheet only if values are valid.
        if ( temp_dht11 == ERROR_VALUE or humid_dht11 == ERROR_VALUE or temp_dht22 == ERROR_VALUE or humid_dht22 == ERROR_VALUE ):
            failCount = failCount+1
            print("values invalid, sheet not updated! failCount: " + str(failCount) )
            #print("values invalid, sheet not updated! " + "T dht11: " + str(temp_dht11) + ", " + "H dht11: " + str(humid_dht11))
            #print("values invalid, sheet not updated! " + "T dht22: " + str(temp_dht22) + ", " + "H dht22: " + str(humid_dht22))
            time.sleep(RETRY_INTERVAL)
        else:
            updateSheet = WriteToSheet(temp_dht11, humid_dht11, temp_dht22, humid_dht22, failCount)
            updateSheet.writeValuesToSheet(creds);
            del updateSheet

            print("T dht11: " + str(temp_dht11) + ", " + "H dht11: " + str(humid_dht11))
            print("T dht22: " + str(temp_dht22) + ", " + "H dht22: " + str(humid_dht22))
            time.sleep(UPDATE_INTERVAL)

main()
