/**************************** weather_esp01_dht_http.ino ***********************

  Description:  Read temperature & humidity from DHT11 & DHT22 sensor.
                ESP-01 acts as webserver.
                Builds webpage with temperature and humidity values.
                Builds webpage with some information about NodeMCU and Sensor.

  Components:   - ESP-01 esp8266 NodeMcu
                - DHT11 or DHT22 temperature and humidity sensor

  The circuit:  - DHT-XX Data -> ESP-01 gpio 0

  IDE & tools:  - Arduino IDE 1.8.8, UBUNTU 18.04 LTS

  Librarys:     - https://github.com/esp8266/Arduino
                - https://github.com/adafruit/DHT-sensor-library
                - https://github.com/adafruit/Adafruit_Sensor

  IDE & tools:  - Arduino IDE 1.8.8, UBUNTU 18.04 LTS

  References:   -
*******************************************************************************/

/*------------------------------------------------------------------------------

    Version 1.0     4'19    Yasperzee
                    Release 2: In synch with weather_esp01_dht_http.py (version 1.0)
                    Is NOT! comatible with 'weather_esp01_dht_http.py version<1.0'

    Version 0.4     4'19    Yasperzee
                    File name changed, DHT22 support added.
                    Some information about node and sensor added to webpage

    Version 0.3     3'19    Yasperzee
                    Cleaning for release

    Version 0.2     2'19    Yasperzee
                    DHT-11 Data pin to ESP-01 gpio 0, removed LED

    Version 0.1     2'19    Yasperzee
                    nodemcuWeather modified to support ESP-01 and DHT-11.

------------------------------------------------------------------------------*/

// includes
#include "ssid.h"  // SSID and PASS strings for local network
#include <Arduino.h>
#include "ESP8266WiFi.h"
#include "DHT.h"

// defines
#define PORT        80
#define BAUDRATE    115200
#define DHT_PIN 	0 // ESP-01 gpio 0
//#define DHT_PIN 	2 // ESP-01 gpio 2

// Select DHT sensor in use,<s values from DHT.h
//#define DHT_TYPE 	DHT11
#define DHT_TYPE 	DHT22

//Select strings for Sensor and Node, used for information and debug
//String SENSOR  =  "DHT-11";
String SENSOR   =  "DHT-22";
String NODEMCU  =  "ESP-01";

#define RETRY_WIFI_TIME     500 //ms

// constants
const float ErrorValue = -999.9;
// variables
String getValuesState   = "off";

// Variable to store the HTTP request
String header;

// values from DHT read_dht_sensor
struct Values
    {
    float temperature;
    float humidity;
    };

// Functions
//Values read_dht11(void);
Values read_dht_sensor(void);
String build_html(void);

// Set web server port number to 80
WiFiServer server(PORT);
// Initialize DHT sensor.
DHT dht(DHT_PIN, DHT_TYPE);

void setup()
    {
    Serial.begin(BAUDRATE);
    // Connect to Wi-Fi network with SSID and password
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
        {
        delay(500);
        Serial.print(".");
        }
    // Print local IP address and start web server
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    server.begin();
    dht.begin();
    Serial.println("Node is " + NODEMCU);
    Serial.println("Sensor is " + SENSOR);
    } // setup

void loop()
    {
    WiFiClient client = server.available();   // Listen for incoming clients

    if (client)
        { // If a new client connects
        Serial.println("New Client.");
        String currentLine = ""; // make a String to hold incoming data from the client
        while (client.connected())
            { // loop while the client's connected
            if (client.available())
                { // if there's bytes to read from the client,
                char c = client.read();
                Serial.write(c);
                header += c;
                if (c == '\n')
                    { // if the byte is a newline character
                    // if the current line is blank, you got two newline characters in a row.
                    // that's the end of the client HTTP request, so send a response:
                    if (currentLine.length() == 0)
                        {
                        Serial.println("Send response");
                        // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
                        // and a content-type so the client knows what's coming, then a blank line:
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/html");
                        client.println("Connection: close");
                        client.println();

                        // GET values
                        if (header.indexOf("GET /TH/on") >= 0)
                            {
                             getValuesState = "on";
                            }
                        else if (header.indexOf("GET /TH/off") >= 0)
                            {
                            getValuesState= "off";
                            }
                        // Send the HTML web page
                        String tmp = build_html();
                        //Serial.println(tmp);
                        client.println(tmp);
                        client.println("Connection closed.");
                        // Break out of the while loop
                        break;
                        } // if (currentLine.length() == 0)
                    else
                        { // if you got a newline, then clear currentLine
                        currentLine = "";
                        }
                    } // if (c == '\n')
                else if (c != '\r')
                    {  // if you got anything else but a carriage return character,
                    currentLine += c; // add it to the end of the currentLine
                    }
                } // if (client.available())
            } // while (client.connected())
        // Clear the header variable
        header = "";
        // Close the connection
        client.stop();
        Serial.println("Client disconnected.");
        Serial.println("");
        }  // if(client)
    } // loop

//Values read_dht11(void)
Values read_dht_sensor(void)
    {
    float T,H;
    Values values;

    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    H = dht.readHumidity();
    // Read temperature as Celsius (the default)
    T = dht.readTemperature();
    values.humidity = H;
    values.temperature = T;
    // Check if any reads failed and exit early (to try again).
    if (isnan(H) || isnan(T))
        {
        Serial.println(F("Failed to read DHT sensor!"));
        values.temperature = ErrorValue;
        values.humidity = ErrorValue;
      	}
    return values;
    }

String build_html(void)
    {
    Values values;
    String webpage;

    webpage  = "<!DOCTYPE html><html>";
    webpage += "<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
    webpage += "<link rel=\"icon\" href=\"data:,\">";
    // CSS to style the on/off buttons
    // Feel free to change the background-color and font-size attributes to fit your preferences
    webpage += "<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}";
    webpage += ".button { background-color: #195B6A; border: none; color: white; padding: 16px 40px;";
    webpage += "text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}";
    webpage += ".button2 {background-color: #77878A;}</style></head>";
    // Web Page Heading

    // Display temperature and pressure values
    if (getValuesState=="off")
        {
        webpage += "<p>Get measurements </p>";
        webpage += "<p><a href=\"/TH/on\"><button class=\"button\">GET</button></a></p>";
        webpage += "<p> Info: ";
        webpage +=  NODEMCU;
        webpage += " / ";
        webpage +=  SENSOR ;
        webpage += "</p>";
        }
    else
        {
        values = read_dht_sensor();
        webpage += "<p>Got measurements </p>";
        webpage += "<p><a href=\"/TH/off\"><button class=\"button button2\">GOT</button></a></p>";
        // Print temperature and humidity values here
        webpage += "<p>Temperature: ";
        webpage += (values.temperature);
        webpage += " °C";
        webpage += "<br/>";
        webpage += "Humidity: ";
        webpage += (values.humidity);
        webpage += " %";
        webpage += "<p>";
        }
    webpage += "</body></html>";
    // The HTTP response ends with another blank line
    webpage += "";

    return (webpage);
    } // build_html
