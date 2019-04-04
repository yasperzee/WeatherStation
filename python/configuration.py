
server_url_dht_01  = 'http://192.168.10.39/'  # Node DHT-01 (with DHT11)
server_url_dht_02  = 'http://192.168.10.57/'  # Node DHT-02 (with DHT22)

# Tags to find values on received html page
tagTemp         = 'Temperature: '
tagHumid        = 'Humidity: '
tagInfo         = 'Info: '

# Get page with Temperature & Humidity values
request_values_url_dht_01  = server_url_dht_01 + 'TH/on'
request_values_url_dht_02  = server_url_dht_02 + 'TH/on'
# Get page with information about node and sensor
request_info_url_dht_01  = server_url_dht_01 + 'TH/off'
request_info_url_dht_02  = server_url_dht_02 + 'TH/off'

ERROR_VALUE = -999.9

# Select sensor and nodemcu
#NODEMCU    = "ESP01"
#SENSOR     = "DHT-11"
#SENSOR     = "DHT-22"
#NODENUMBER = "01"

SHEET_NAME      = 'DHT-COMP' # two nodes to same sheet

#The ID of a spreadsheet.
SPREADSHEET_ID  = '1bZ0gfiIlpTnHn-vMSA-m9OzVQEtF1l7ELNo40k0EBcM'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#NODE_ID    = NODEMCU + '_' + SENSOR + '_' + NODENUMBER
#SHEET_NAME = NODE_ID


info_range_name_dht11 = SHEET_NAME + '!C1' # DHT11
info_range_name_dht22 = SHEET_NAME + '!E1' # DHT22
info_range_name_fail_count = SHEET_NAME + '!A1'

# Defines
MIN_ROW     = 3
MAX_ROW     = 96 + MIN_ROW # 15min update interval => 96 records / day
