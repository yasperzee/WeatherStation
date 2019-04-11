#!/usr/bin/ python3

"""------------------------------ Version history ------------------------------

    v0.2    yasperzee   4'19    Read 3 sensors to sheet
    v0.1    yasperzee   4'19    Classes moved to separate modules
            Configurations for weather_esp01_dht_http.py
-----------------------------------------------------------------------------"""

server_url_dht_01  = 'http://192.168.10.39/'  # Node-01 (with DHT11)
server_url_dht_02  = 'http://192.168.10.54/'  # Node-02 (with DHT11)
server_url_dht_03  = 'http://192.168.10.57/'  # Node-03 (with DHT22)

# Tags to find values on received html page
tagTemp         = 'Temperature: '
tagHumid        = 'Humidity: '
tagInfo         = 'Info: '

# Get page with Temperature & Humidity values
request_values_url_dht_01  = server_url_dht_01 + 'TH/on'
request_values_url_dht_02  = server_url_dht_02 + 'TH/on'
request_values_url_dht_03  = server_url_dht_03 + 'TH/on'
# Get page with information about node and sensor
request_info_url_dht_01  = server_url_dht_01 + 'TH/off'
request_info_url_dht_02  = server_url_dht_02 + 'TH/off'
request_info_url_dht_03  = server_url_dht_03 + 'TH/off'

SHEET_NAME      = 'DHT-COMP' # three nodes to same sheet

#The ID of a spreadsheet.
SPREADSHEET_ID  = '1bZ0gfiIlpTnHn-vMSA-m9OzVQEtF1l7ELNo40k0EBcM'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

info_range_name_dht11_01 = SHEET_NAME + '!C1' # dht11_01
info_range_name_dht11_02 = SHEET_NAME + '!E1' # dht11_02
info_range_name_dht22_01 = SHEET_NAME + '!G1' # dht22_01
#info_range_name_fail_count = SHEET_NAME + '!A1'

MIN_ROW     = 3
MAX_ROW     = 96 + MIN_ROW # 15min update interval => 96 records / day
ERROR_VALUE = -999.9
