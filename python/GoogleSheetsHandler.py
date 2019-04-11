#!/usr/bin/ python3

"""------------------------------ Version history ------------------------------

    v0.2    yasperzee   4'19    Read 3 sensors to sheet
    v0.1    yasperzee   4'19    Classes moved to separate modules
            Classes to write sensor data to sheet for weather_esp01_dht_http.py
-----------------------------------------------------------------------------"""

import os.path
import pickle
import datetime

# Install Googleapiclient for python3 with pip3
from googleapiclient.discovery import build
# Install google-assistant-sdk for python3 with pip3
# Install google-auth-oauthlib for python3 with pip3
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from configuration import *

class WriteToSheet:

    #def __init__(self, temp1, humid1, temp2, humid2, failCount):
    #def __init__(self, temp1, humid1, temp2, humid2, temp3, humid3, failCount):
    def __init__(self, temp1, humid1, temp2, humid2, temp3, humid3):
        self.temp1 = temp1
        self.humid1 = humid1
        self.temp2 = temp2
        self.humid2 = humid2
        self.temp3 = temp3
        self.humid3 = humid3
        #self.failCount = failCount
        self.info1 = ""
        self.info2 = ""
        self.info3 = ""

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
            htmlPage   = response.read()
            encoding   = response.headers.get_content_charset('utf-8')
            stringPage = htmlPage.decode(encoding)

    def writeInfoToSheet(self, creds, info1, info2, info3):
        self.creds = creds
        self.info1  = info1
        self.info2  = info2
        self.info3  = info3
        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        # Build the service object
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')
        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')

        # Write info1 to 'info_range_name'
        request =   service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range = info_range_name_dht11_01,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[ self.info1 ]]})
        request.execute()

        # Write info1 to 'info_range_name'
        request =   service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range = info_range_name_dht11_02,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[ self.info2 ]]})
        request.execute()

        # Write info2 to 'info_range_name'
        request =   service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range = info_range_name_dht22_01,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[ self.info3 ]]})
        request.execute()

    def writeValuesToSheet(self, creds):
        self.creds = creds

        # Supported APIs w/ versions: https://developers.google.com/api-client-library/python/apis/
        # https://developers.google.com/sheets/api/
        # Build the service object
        service = build('sheets', 'v4', credentials=self.creds)
        if service == 0:
            print('build FAIL!')

        spreadsheet = service.spreadsheets() # Returns the spreadsheets Resource.
        if spreadsheet == 0:
            print('service FAIL!')

        # Read data-area to move, result type is "Value Range"
        results =   spreadsheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    #range = (SHEET_NAME + '!A'+ str(MIN_ROW) + ':' + 'D' + str(MAX_ROW))).execute() # DHT11 or DTH22
                    #range = (SHEET_NAME + '!A'+ str(MIN_ROW) + ':' + 'F' + str(MAX_ROW))).execute() # DHT11 and DHT22
                    range = (SHEET_NAME + '!A'+ str(MIN_ROW) + ':' + 'H' + str(MAX_ROW))).execute() # DHT11_01, DHT11_02 and DHT22_01

        data_to_paste = results.get('values', [])
        # Write data-area back to position MIN_ROW+1
        request = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range = (SHEET_NAME + '!A'+ str(MIN_ROW+1)),
            valueInputOption='USER_ENTERED',
            body={'values': data_to_paste}).execute()

        # Clear row MAX_ROW+1
        request =   service.spreadsheets().values().clear(
                    spreadsheetId=SPREADSHEET_ID,
                    #range = (SHEET_NAME + '!A'+ str(MAX_ROW+1) + ':' + 'D' + str(MAX_ROW+1))).execute()  # DHT11 or DTH22
                    #range = (SHEET_NAME + '!A'+ str(MAX_ROW+1) + ':' + 'F' + str(MAX_ROW+1))).execute()  # DHT11 and DTH22
                    range = (SHEET_NAME + '!A'+ str(MAX_ROW+1) + ':' + 'H' + str(MAX_ROW+1))).execute() # DHT11_01, DHT11_02 and DHT22_01


        # get date and time
        d_format = "%d-%b-%Y"
        t_format = "%H:%M"
        now = datetime.datetime.today()
        today = now.strftime(d_format)
        time = now.strftime(t_format)
        print(today + " " + time)

        # update date, time and values to the first row in data-area
        result = service.spreadsheets().values().update(
                        spreadsheetId = SPREADSHEET_ID,
                        range= SHEET_NAME + '!A'+ str(MIN_ROW),
                        valueInputOption='RAW',
                        #body={'values': [[ today, time, self.temp, self.humid ]]}).execute()
                        #body={'values': [[ today, time, self.temp1, self.humid1, self.temp2, self.humid2 ]]}).execute()
                        body={'values': [[ today, time, self.temp1, self.humid1, self.temp2, self.humid2, self.temp3, self.humid3 ]]}).execute()

        # Write failCount to sheet
        """
        global failCount
        request =   service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range = info_range_name_fail_count,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[ self.failCount ]]})
        request.execute()
        """
    def setTemp(temp):
        # add temp to sheet
        return self.temp

    def setHumid(humid):
        # add humid to sheet
        return self.humid

    #def setFailCount(failCount):
    #    self.failCount = failCount

    def getInfo():
        return self.info



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
