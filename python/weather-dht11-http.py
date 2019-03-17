#!/usr/bin/ python3
#
#*******  weather-dht11-http.py     Usage: python3 weather-dht11-http.py *******
#
#               Technology demo using http. ESP-01 as web-server.
#               This script reads temperature and humidity from DHT-11 sensor
#               connected to ESP-01 and updates valid values to google sheet.
#
#   TODO:       * Add failsafe incase server not available
#               * Update sheet automaticly with timer,
#                 so run script on raspberrypi by cron or something. . .
#               * Build QT app to call this script
#
#   FIXME:      Nice to have:   * Should work with python2.7 also ???
#                                   -> some issues with urllib on python2.7
#
#   v0.2        yasperzee   3'19    update
#                   * Manipulate sheet so that NEW value is written to top row
#                       --> Show on meters latest measured temperature & humidity
#                       move rows down by one, delete row MAX_ROW+1, write values to top row
#                   * if sensorValue == ERROR_VALUE, do NOT send ERROR_VALUE to sheet
#
#   v0.1        yasperzee   3'19    modified for dht11 sensor
#
#   v0.5        yasperzee   2'19    Some robustnest added to handle sensor values
#                                   Add new values to next empty row.
#                                   Added table and some visualization to sheet
#
#   v0.4        yasperzee   2'19    Update sheets with values
#                                   Add current date and time to sheet with values
#
#   v0.3        yasperzee   2'19    Initial suppport for send values to sheeet
#                                   Connects to googlesheets and read some values
#
#   v0.2        yasperzee   2'19    Support for nodemcu_weather v0.3, update tagPres accordingly
#
#   v0.1        yasperzee   2'19    Read webpage with sensor values
#                                   combatible with nodemcu_weather v0.2
#
#*******************************************************************************
from __future__ import print_function
import datetime
import pickle
import os.path
import time
# Install Googleapiclient for python3 with pip3
from googleapiclient.discovery import build
# Install google-assistant-sdk for python3 with pip3
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from urllib.request import urlopen

# Get page with Temperature & Barometer values
request_url     = 'http://192.168.10.39/4/on' # home
#request_url     = 'http://192.168.10.39/4/on' # mobile

# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Sheet WeatherHerwood
# The ID and range of a spreadsheet.
SPREADSHEET_ID  = '1bZ0gfiIlpTnHn-vMSA-m9OzVQEtF1l7ELNo40k0EBcM'
SHEET_NAME      = 'DHT11_01!'
MIN_ROW = 3
MAX_ROW = 96 + MIN_ROW # 15min update interval => 96 readings / day
DATA_RANGE      = 'A'+str(MIN_ROW)+':'+'D'+str(MAX_ROW)
RANGE_NAME = SHEET_NAME + DATA_RANGE
RETRY_INTERVAL  = 10    #2*60 # 2min.
UPDATE_INTERVAL = 5     #15*60 # 15min.
ERROR_VALUE     = -999.9

# Tags to find values on received html page
# !!!! Must be updated ONLY together with nodemcu_weather software,
# so must match literally with tags in nodemcu weatherserver response!!!
# The SPACE after ':' is MANDATORY!
tagTemp         = 'Temperature: '
tagHumid        = 'Humidity   : '
#*******************************************************************************
class SensorValuesDHT11:
    # Constructor
    def __init__(self):
        # MAX value lenght is xxxx.xx (Barometer)
        self.valLen = 8
        # Parsed sensor values (float)
        self.temperatureVal  = 0
        self.humidityVal     = 0

    # Destructor
    def __del__(self):
       class_name = self.__class__.__name__

    def readSensors(self):
        # Get webpage with sensor values
        with urlopen(request_url) as response:
            htmlPage = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)
            # Print Decoded page
            # print(stringPage)
            # print('')

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
#*******************************************************************************
#*******************************************************************************
class Gredentials:
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first time.

    # Constructor
    def __init__(self):
        self.creds = None

    # Destructor
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
#*******************************************************************************
class ValuesToSheet:
    # Constructor
    def __init__(self, temp, humid):
        self.temp = temp
        self.humid = humid
    # Destructor
    def __del__(self):
        class_name = self.__class__.__name__

    def readSheet(self, creds):
        self.creds = creds
        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')
        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')
        with urlopen(request_url) as response:
            htmlPage = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)

    def writeSheet(self, creds):
        self.creds = creds
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
#*******************************************************************************
#*******************************************************************************
def main():
    while 1:
        # If token.pickle does not exists, create newone.
        istoken = Gredentials()
        istoken.getToken();
        creds = istoken.creds
        del istoken

        # Read current Temperature & Barometer values
        sval = SensorValuesDHT11()
        sval.readSensors();
        temp = sval.getTemp()
        humid = sval.getHumid()
        del sval

        # Append values to spreadsheet only if values are valid
        if ( temp == ERROR_VALUE or humid == ERROR_VALUE ):
            print("values invalid, sheet not updated! " + "T:" + str(temp) + ", " + "H:" + str(humid))
            time.sleep(RETRY_INTERVAL)
        else:
            updateSheet = ValuesToSheet(temp, humid)
            updateSheet.writeSheet(creds);
            del updateSheet
            print("T: " + str(temp) + ", " + "H: "+str(humid))
            # sleep update_interval
            time.sleep(UPDATE_INTERVAL)
    #*******************************************************************************

main()
