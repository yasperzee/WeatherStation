#!/usr/bin/ python3
#
#***** weather_esp01_dht_http.py  Usage: python3 weather_esp01_dht_http.py *****
#
#       Technology demo using http. ESP-01 as web-server.
#       This script reads temperature and humidity from DHT-11 or DHT-22 sensor
#       connected to ESP-01 and updates valid values to google sheet.
#
#*******************************************************************************

#TODO:      * Add failreading count to sheet when ERROR_VALUE read
#TODO:      * Add failsafe incase server not available
#TODO:      * Add retry / failsafe incase server and/or sheet gets unavailable
#TODO:      * Should write to selected/named sheet on spreadsheet, not to spreadsheet which is first sheet.

"""--------- Version history ---------------------------------------------------

    v1.0    yasperzee   4'19  Release 2: In synch with weather_esp01_dht_http.ino (version 1.0)
            Is NOT! compatible with 'weather_esp01_dht_http.ino version<1.0'
                Filename changed.
                Get node and sensor info.
                Some support for DHT-22 - Not really relavant here...

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
from __future__ import print_function
import datetime
import pickle
import os.path
import time
# Install Googleapiclient for python3 with pip3
from googleapiclient.discovery import build
# Install google-assistant-sdk for python3 with pip3
# Install google-auth-oauthlib for python3 with pip3
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from urllib.request import urlopen

################################ CONFIGURATIONS #################################
                                                                                #
#server_url  = 'http://192.168.10.39/'  # Node DHT_01 (with DHT11)              #
server_url  = 'http://192.168.10.57/'  # Node DHT_02 (with DHT22)               #
                                                                                #
# If modifying these scopes, delete the file token.pickle.                      #
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']                       #
                                                                                #
# spreadsheet's name is WeatherHerwood                                          #
# The ID and range of a spreadsheet.                                            #
SPREADSHEET_ID  = '1bZ0gfiIlpTnHn-vMSA-m9OzVQEtF1l7ELNo40k0EBcM'                #
                                                                                #
RETRY_INTERVAL = 3*60   # 3min retry if sensor reading(s) == ERROR_VALUE        #
UPDATE_INTERVAL= 15*60  # 15min -> 96 records / 24h                             #          #
                                                                                #
#################################################################################

# Get page with Temperature & Humidity values
request_values_url  = server_url + 'TH/on'
# Get page with information about node and sensor
request_info_url  = server_url + 'TH/off'
MIN_ROW = 3
MAX_ROW = 96 + MIN_ROW # 15min update interval => 96 records / day
ERROR_VALUE     = -999.9

# Select sensor and node
#SENSOR = "DHT11"
#SENSOR = "DHT22"
#NODE = "ESP-01"

#SHEET_NAME      = SENSOR + '_01!'
#SHEET_NAME      = NODE + "_" + SENSOR
#DATA_RANGE      = 'A'+str(MIN_ROW)+':'+'D'+str(MAX_ROW)
#RANGE_NAME = SHEET_NAME + DATA_RANGE

# global variables
once = False;

# Tags to find values on received html page
# !!!! Must be updated ONLY together with nodemcu_weather software,
# so must match literally with tags in nodemcu weatherserver response!!!
# The SPACE after ':' is MANDATORY!
tagTemp         = 'Temperature: '
tagHumid        = 'Humidity: '
tagInfo         = 'Info: '

#*******************************************************************************
class SensorDHT:

    def __init__(self):
        # MAX value lenght is xxxx.xx (Barometer)
        self.valLen = 8
        # Parsed sensor values (float) & info (string)
        self.temperatureVal = 0
        self.humidityVal    = 0
        self.info           = ""

    def __del__(self):
       class_name = self.__class__.__name__

    def readInfo(self):
        # Get webpage with information about node and sensor
        with urlopen(request_info_url) as response:
            htmlPage = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)
            # Print Decoded page
            #print(stringPage)
            #print('')

        # Information
        tagIndex = stringPage.find(tagInfo)
        infoIndex = stringPage.find("</p></body></html>")
        infoStr = (stringPage[tagIndex:infoIndex])
        self.info = infoStr

    def readSensors(self):
        # Get webpage with sensor values
        with urlopen(request_values_url) as response:
            htmlPage = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)
            # Print Decoded page
            #print(stringPage)
            #print('')

        # Temperature
        tagIndex = stringPage.find(tagTemp) + len(tagTemp)
        valIndex = tagIndex + self.valLen
        valueStr = (stringPage[tagIndex:valIndex])
        idx=0
        for x in valueStr:
            idx = idx+1
            if valueStr[idx] == " ":
                valueStr = valueStr[:idx]
                break
        self.temperatureVal = float(valueStr)

        # Humidity
        tagIndex = stringPage.find(tagHumid) + len(tagHumid)
        valIndex = tagIndex + self.valLen
        valueStr = (stringPage[tagIndex:valIndex])
        idx=0
        for x in valueStr:
            idx = idx+1
            if valueStr[idx] == " ":
                valueStr = valueStr[:idx]
                break
        self.humidityVal= float(valueStr)

    def getTemp(self):
        return self.temperatureVal

    def getHumid(self):
        return self.humidityVal

    def getInfo(self):
        return self.info

#*******************************************************************************
class Gredentials:
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first time.

    def __init__(self):
        self.creds = None

    def __del__(self):
       class_name = self.__class__.__name__

    def getToken(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token: pickle.dump(self.creds, token)

    def readToken(self):
        return self.token

#*******************************************************************************
class WriteToSheet:

    def __init__(self, temp, humid):
        self.temp = temp
        self.humid = humid
        self.info = ""

    def __del__(self):
        class_name = self.__class__.__name__

    def readSheet(self, creds):
        self.creds = creds
        #print('Entering readSheet')
        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')
        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')
        with urlopen(request_values_url) as response:
            htmlPage = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)

    def writeInfoToSheet(self, creds, info):
        self.creds = creds
        self.info = info
        #print('Entering writeValuesToSheet')
        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')
        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')

        # Write info to shell A1
        request = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range = ('A1'),
            valueInputOption='USER_ENTERED',
            body={'values': [[ self.info ]]}).execute()

    def writeValuesToSheet(self, creds):
        self.creds = creds
        #print('Entering writeValuesToSheet')
        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')
        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')
        # get date and time
        d_format = "%d-%b-%Y"
        t_format = "%H:%M"
        now = datetime.datetime.today()
        today = now.strftime(d_format)
        time = now.strftime(t_format)
        print(today + " " + time)

        # Read data-area, result type is "Value Range"
        results = spreadsheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range = ('A'+ str(MIN_ROW) + ':' + 'D' + str(MAX_ROW))).execute()
        data_to_paste = results.get('values', [])

        # Write data-area back to position MIN_ROW+1
        request = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range = ('A'+ str(MIN_ROW+1)),
            valueInputOption='USER_ENTERED',
            body={'values': data_to_paste}).execute()

        # Clear row MAX_ROW+1
        request = service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range = ('A'+ str(MAX_ROW+1) + ':' + 'D' + str(MAX_ROW+1))).execute()

        # update date, time and values to the first row in data-area
        result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range='A'+ str(MIN_ROW), valueInputOption='RAW',
        body={'values': [[ today, time, self.temp, self.humid ]]}).execute()

    def setTemp(temp):
        # add temp to sheet
        return self.temp

    def setHumid(humid):
        # add humid to sheet
        return self.humid

    def getInfo():
        return self.info

#*******************************************************************************
def main():
    global once
    while 1:
        if once == False:
            #print('Run only once')
            # If token.pickle does not exists, create newone.
            istoken = Gredentials()
            istoken.getToken();
            creds = istoken.creds
            del istoken

            # Read Node and Sensor information
            ival = SensorDHT()
            ival.readInfo();
            info  = ival.getInfo()
            print("Info: " + info)
            del ival

            # Write info to sheet
            updateSheet = WriteToSheet(ERROR_VALUE, ERROR_VALUE)
            updateSheet.writeInfoToSheet(creds, info);
            del updateSheet
            once = True

        # Read current Temperature & Barometer values
        sval = SensorDHT()
        sval.readSensors();
        temp  = sval.getTemp()
        humid = sval.getHumid()
        del sval

        # Append values to spreadsheet only if values are valid.
        if ( temp == ERROR_VALUE or humid == ERROR_VALUE ):
            print("values invalid, sheet not updated! " + "T:" + str(temp) + ", " + "H:" + str(humid))
            time.sleep(RETRY_INTERVAL)
        else:
            updateSheet = WriteToSheet(temp, humid)
            updateSheet.writeValuesToSheet(creds);
            del updateSheet
            print("T: " + str(temp) + ", " + "B: "+str(humid))
            time.sleep(UPDATE_INTERVAL)

main()
