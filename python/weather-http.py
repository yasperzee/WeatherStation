#!/usr/bin/ python3
#
#*************  weather.py     Usage: python3 weather-http.py ***********************
#
#   TODO:       * Add failsafe incase server not available
#               * Update sheet automaticly with timer,
#                 so run script on raspberrypi by cron or something. . .
#               * Branch: MQTT
#
#   FIXME:      Nice to have:   * Should work with python2.7 also ???
#                                 some issues with urllib on python2.7
#               Mandatory:      * Meters on sheet should show LATEST values.
#
#   v0.5        yasperzee   2'19    Some robustnest added to handle sensor values
#                                   Add new values to next empty row.
#                                   Added table and some visualization to sheet
#
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
# Install Googleapiclient for python3 with pip3
from googleapiclient.discovery import build
# Install google-assistant-sdk for python3 with pip3
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from urllib.request import urlopen

# Get page with Temperature & Barometer values
request_url     = 'http://192.168.10.47/4/on'

# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Sheet WeatherHerwood
# The ID and range of a spreadsheet.
SPREADSHEET_ID  = '1bZ0gfiIlpTnHn-vMSA-m9OzVQEtF1l7ELNo40k0EBcM'
SHEET_NAME      = 'BMP-180_01!'
MIN_ROW = 3
DATA_RANGE      = 'A'+str(MIN_ROW)
#RANGE_NAME      = 'BMP-180_01!A1:E17'
RANGE_NAME = SHEET_NAME + DATA_RANGE
#MAX_ROW = 50
MAX_ROW = 24

# Tags to find values on received html page
# !!!! Must be updated ONLY together with nodemcu_weather software,
# so must match literally with tags in nodemcu weatherserver response!!!
# The SPACE after ':' is MANDATORY!
tagTemp        = 'Temperature: '
#tagPres        = 'Absolute pressure ' # for nodemcu_weather v0.2
tagPres        = 'Barometer  : ' # for nodemcu_weather v0.3

#*******************************************************************************
class SensorValues:
    # Constructor
    def __init__(self):
        # MAX value lenght is xxxx.xx (Barometer)
        self.valLen = 8
        # Parsed sensor values (float)
        self.temperatureVal  = 0
        self.pressureVal     = 0

    # Destructor
    def __del__(self):
       class_name = self.__class__.__name__
       #print (class_name, "destroyed")

    def readSensors(self):
        # Get webpage with sensor values
        with urlopen(request_url) as response:
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
        #print (tagTemp, valueStr)
        # Barometer
        tagIndex = stringPage.find(tagPres) + len(tagPres)
        valIndex = tagIndex + self.valLen
        valueStr = (stringPage[tagIndex:valIndex])
        for x in valueStr:
            idx = idx+1
            if valueStr[idx] == " ":
                valueStr = valueStr[:idx]
                break
        self.pressureVal= float(valueStr)
        #print (tagPres, valueStr)

    def getTemp(self):
        return self.temperatureVal

    def getBaro(self):
        return self.pressureVal
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
    def __init__(self, temp, baro):
        self.temp = temp
        self.baro = baro
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
            # Print Decoded page
            #print(stringPage)
            #print('')

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

        # Read the row index on cell 'A1' and increment it by one
        result = spreadsheet.values().get(spreadsheetId=SPREADSHEET_ID,range='A1').execute()
        curr_row = result.get('values', [])
        next_row = int(curr_row[0][0])
        if next_row > MAX_ROW:
            next_row = MIN_ROW
        NEXT_ROW = 'A'+str(next_row)
        next_row = next_row + 1
        result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range='A1', valueInputOption='USER_ENTERED',
        body={'values': [[next_row]]}).execute()

        #update date, time and values to next row
        result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=NEXT_ROW, valueInputOption='RAW',
        body={'values': [[ today, time, self.temp, self.baro ]]}).execute()

    def setTemp(temp):
        # add temp to sheet
        return self.temp

    def setBaro(baro):
        # add baro to sheet
        return self.baro
#*******************************************************************************
#*******************************************************************************
def main():
    # If token.pickle does not exists, create newone.
    istoken = Gredentials()
    istoken.getToken();
    creds = istoken.creds
    del istoken

    # Read current Temperature & Barometer values
    sval = SensorValues()
    sval.readSensors();
    temp = sval.getTemp()
    baro = sval.getBaro()
    del sval

    # Append values to spreadsheet
    updateSheet = ValuesToSheet(temp, baro)
    #updateSheet.readSheet(creds);
    updateSheet.writeSheet(creds);
    del updateSheet

    print("T: " + str(temp) + ", " + "B: "+str(baro))
#*******************************************************************************

main()
