/***************************** nodemcu-weather-http.ino *****************************
#
# Location:         ---- path to github ----
#
# Description:      Reads temperature & pressure from bmp180 sensor,
#                   Acts as webserver, builds webpage with temperature and Barometer values
#
# Components:   - LoLin v3 esp8266 NodeMcu
#               - BMP180 sensor w/ temperature and barometer
#
# The circuit:  - bmp180 -> NodeMcu:   SCL -> D1(gpio5), SDA -> D2(gpio4)
#
# Librarys:     - git clone https://github.com/sparkfun/BMP180_Breakout
#               - https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WiFi
#
# References:   -
#
#-------------------------------------------------------------------------------
#
#   TODO:           * Add support for BME280 sensor w/ temperature, humidity & barometer.
#                   * Add support for DHT11 sensor w/ temerature and humidity
#                   * Cleanup webpage, remove LED control etc
#                   * Send local IP to dedicated e-mail after 1. connect
#
#   Version 0.4     Yasperzee   2'19
#                   Some additional comments etc
#
#   Version 0.3     Yasperzee   2'19
#                   Header updated, webpage cleaned, pressure Tag corrected,
#                   values rounded to one decimal
#
#   Version 0.2     Yasperzee   2'19
#                   Cleaned, added build_html & read_bmp180 functions.
#
#   Version 0.1     Yasperzee   2'19
#                   Server functionality tested.
#
*******************************************************************************/
// includes
#include "ssid.h"  // SSID and PASS strings for local network
#include <ESP8266WiFi.h>
#include <SFE_BMP180.h>

// defines
// #define ALTITUDE 119.0 // Altitude of Tampere-Pirkkala airport, Finland. in meters
#define ALTITUDE 129.0 // Altitude of Kalkunvuori, Tampere Finland, in meters

// constants
const int i2c_sda = 4;
const int i2c_scl = 5;
const int intLed  = 2; // LoLin v3 node mcu internal LED.

// variables
String intLedState     = "off";
String getValuesState  = "off";

// Variable to store the HTTP request
String header;

// values from BMP180
struct Values
    {
    double temperature;
    double pressure;
    };

// Functions
Values read_bmp180(void);
String build_html(void);

// Set web server port number to 80
WiFiServer server(80);
SFE_BMP180 bmp180;

void setup()
{
    Serial.begin(115200);
    // Initialize the output variables as outputs
    pinMode(intLed,  OUTPUT);
    // internal LED: HIGH -> Led OFF
    digitalWrite(intLed,  HIGH);
    // Connect to Wi-Fi network with SSID and password
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
        {
        Values values;
        delay(500);
        Serial.print(".");
        }
    // Print local IP address and start web server
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    server.begin();
    Wire.begin(i2c_sda, i2c_scl);
    // Initialize the sensor (it is important to get calibration values stored on the device).
    if (bmp180.begin() == 0)
        {
        Serial.println("BMP180 init FAIL!!");
        }
} // setup_

void loop()
{
Values values;
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
                    // turns the GPIOs on and off
                    if (header.indexOf("GET /5/on") >= 0)
                        {
                        Serial.println("intLed on");
                        intLedState  = "on";
                        digitalWrite(intLed, LOW);
                        }
                    else if (header.indexOf("GET /5/off") >= 0)
                        {
                        Serial.println("intLed off");
                        intLedState  = "off";
                        digitalWrite(intLed, HIGH);
                        }
                    else if (header.indexOf("GET /4/on") >= 0)
                        {
                         // Serial.println("Get measurements 1");
                         getValuesState = "on";
                        }
                    else if (header.indexOf("GET /4/off") >= 0)
                        {
                        // Serial.println("Get measurements 2");
                        getValuesState= "off";
                        }
                    // Send the HTML web page
                    String tmp = build_html();
                    //Serial.println(tmp);
                    client.println(tmp);
                    client.println("Connection: close");
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

Values read_bmp180()
{
    char bmp180_status;
    double T,P,p0,a;
    Values values;

    bmp180_status = bmp180.startTemperature();

    if (bmp180_status != 0)
        {
        // Wait for the measurement to complete:
        delay(bmp180_status);
        // Retrieve the completed temperature measurement:
        // Note that the measurement is stored in the variable T.
        // Function returns 1 if successful, 0 if failure.
        bmp180_status = bmp180.getTemperature(T);
        //values.temperature = T;
        values.temperature = round(T*10)/10.0; // round to one decimal
        if(bmp180_status == 0)
            {
            values.temperature = -99,99;
            Serial.println("startTemperature FAILED!!!");
            }
        }
    else
        {
        values.temperature = -99,99;
        Serial.println("getTemperature FAILED!!!");
        }
    bmp180_status = bmp180.startPressure(3);
    if (bmp180_status != 0)
        {
        // Wait for the measurement to complete:
        delay(bmp180_status);
        // Retrieve the completed pressure measurement:
        // Note that the measurement is stored in the variable P.
        // Note also that the function requires the previous temperaturmeasurement (T).
        // (If temperature is stable, you can do one temperature measurement for number of pressure measurements.)
        // Function returns 1 if successful, 0 if failure.
        bmp180_status = bmp180.getPressure(P,T);
        //values.pressure = P;
        values.pressure = round(P*10)/10.0; // round to one decimal
        if(bmp180_status == 0)
            {
            values.pressure = -99,99;
            Serial.println("getPressure FAILED!!!");
            }
        }
        else
            {
            values.pressure = -99,99;
            Serial.println("startPressure FAILED!!!");
            }
            //p0 = bmp180.sealevel(P,ALTITUDE); // we're at ALTIDUDE meters
            //a = bmp180.altitude(P,p0); // Calculated altitude
/* DEBUG
    Serial.print("Temperature:      ");
    Serial.print(values.temperature);
    Serial.print(" °C");
    Serial.print("\n");
    Serial.print("Absolute pressure ");
    Serial.print(values.pressure);
    Serial.print(" hPa/mbar");
    Serial.print("\n");
DEBUG */
    return values;
} //read_bmp180

String build_html(void)
{ // returns String webpage
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
    // Display current state, and ON/OFF buttons for internal LED
    webpage += "<p>IntLed - State " + intLedState + "</p>";
    // If the intLedState is off, it displays the ON button
    if (intLedState=="off")
        {
        webpage += "<p><a href=\"/5/on\"><button class=\"button\">ON</button></a></p>";
        }
    else
        {
        webpage += "<p><a href=\"/5/off\"><button class=\"button button2\">OFF</button></a></p>";
        }
    // Display temperature and pressure values
    if (getValuesState=="off")
        {
        webpage += "<p>Get measurements </p>";
        webpage += "<p><a href=\"/4/on\"><button class=\"button\">GET</button></a></p>";
        webpage += "<p> temperature and pressure values here </p>";
        }
    else
        {
        values = read_bmp180();
        webpage += "<p>Got measurements </p>";
        webpage += "<p><a href=\"/4/off\"><button class=\"button button2\">GOT</button></a></p>";
        // Print temperature and presure values here
        webpage += "<p>Temperature: ";
        webpage += (values.temperature);
        webpage += " °C";
        webpage += "<br/>";
        webpage += "Barometer  : ";
        webpage += (values.pressure);
        webpage += " hPa/mbar";
        webpage += "<p>";
        }
    webpage += "</body></html>";
    // The HTTP response ends with another blank line
    webpage += "";

    return (webpage);
}
