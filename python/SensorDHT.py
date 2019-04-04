#*******************************************************************************

from urllib.request import urlopen

from configuration import *

class Sensor_DHT:
    def __init__(self, request_url):
        self.request_url = request_url
        # MAX value lenght is xxxx.xx (Barometer)
        self.valLen = 8
        # Parsed sensor values (float)
        self.temperatureVal = 0
        self.humidityVal    = 0
        self.info           = ""

    def __del__(self):
       class_name = self.__class__.__name__

    def readInfo(self):
        # Get webpage with information about node and sensor
        #with urlopen(request_info_url_dht_01) as response:
        with urlopen(self.request_url) as response:
            htmlPage    = response.read()
            encoding    = response.headers.get_content_charset('utf-8')
            stringPage  = htmlPage.decode(encoding)
            # Print Decoded page
            #print(stringPage)
            #print('')

        # Information
        tagIndex    = stringPage.find(tagInfo)
        infoIndex   = stringPage.find("</p></body></html>")
        infoStr     = (stringPage[tagIndex:infoIndex])
        self.info   = infoStr

    def readSensors(self):
        # Get webpage with sensor values
        with urlopen(self.request_url) as response:
            htmlPage    = response.read()
            encoding    = response.headers.get_content_charset('utf-8')
            stringPage  = htmlPage.decode(encoding)
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
