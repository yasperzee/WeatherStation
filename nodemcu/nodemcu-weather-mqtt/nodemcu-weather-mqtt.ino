  /*************************** nodemcu-weather-mqtt.ino *****************************
  #
  # Description:    mqtt client reads temperature & pressure from bmp180 sensor.
  #
  #                 By yasperzee 2019
  #
  # Components:   - esp8266 node mcu
  #               - BMP180 sensor
  #
  # The circuit:  - bmp180:   SCL-> D1(gpio5), SDA-> D2(gpio4)
  #
  # Librarys:     - git clone https://github.com/sparkfun/BMP180_Breakout
  #               - https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WiFi
  #                 <PubSubClient.h>
  #
  # References:   -
  #
  *****************************************************************************/

/* ----------Version history ---------------------------------------------------
# TODO: sleep

    Version 0.1     Yasperzee   2'19
                    mqtt client functionality tested.
    TODO: update to BSE280 sensor w/ temperature, humidity & pressure.

------------------------------------------------------------------------------*/

// includes
#include "ssid.h"  // SSID and PASS strings for local network
#include <ESP8266WiFi.h>
#include <SFE_BMP180.h>
#include <PubSubClient.h>

// defines
#define ALTITUDE 129.0 // Altitude of Kalkunvuori, Tampere Finland. in meters
#define MQTT_SERVER "192.168.10.52" // Local Rpi3 with mosquitto
#define VARIABLE_LABEL "temperature-sensor" // Assing the variable label
#define VARIABLE_LABEL_SUBSCRIBE "temperature" // Assing the variable label
#define DEVICE_LABEL "BMP180_01" // Assig the device label
#define TOKEN ""
#define MQTT_CLIENT_NAME "node_01"    // MQTT client Name, please enter your own 8-12 alphanumeric character ASCII string;
                                        // it should be a random and unique ascii string and different from all other devices

// constants
//const char mqttBroker[]  = "192.168.10.52"; // Local Rpi3 with mosquitto
const int PUBLISH_INTERVAL  = 10000; // intervall to publish
const int RECONNECT_DELAY   = 5000; // Try to reconnect mqtt server
const int i2c_sda = 4;
const int i2c_scl = 5;
const int intLed  = 2; // LoLin v3 node mcu internal LED.

// variables
char payload[100];
char topic[150];
char topicSubscribe[100];
// Space to store values to send
char str_sensor[10];

// values from BMP180
struct Values
    {
    int num_of_sensors = 2;
    double temperature;
    double pressure;
    };

// Function declarations
Values read_bmp180(void);
void reconnect();
void publish(Values);
void callback(char* topic, byte* payload, unsigned int length);

SFE_BMP180 bmp180;
WiFiClient mqtt_client;
PubSubClient client(mqtt_client);

void setup()
{
    Serial.begin(115200);
    // Initialize the output variables as outputs
    pinMode(intLed,  OUTPUT);
    // internal LED: HIGH -> Led OFF
    digitalWrite(intLed,  HIGH);
    // Connect to Wi-Fi network with SSID and password
    WiFi.begin(ssid, password);
    Serial.print("Connecting to ");
    Serial.println(ssid);
    while (WiFi.status() != WL_CONNECTED)
        {
        Values values;
        delay(500);
        Serial.print(".");
        }
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    //client.setServer(mqttBroker, 1883);
    client.setServer(MQTT_SERVER, 1883);
    client.setCallback(callback);
    sprintf(topicSubscribe, "/v1.6/devices/%s/%s/lv", DEVICE_LABEL, VARIABLE_LABEL_SUBSCRIBE);
    client.subscribe(topicSubscribe);

    Wire.begin(i2c_sda, i2c_scl);
    // Initialize the sensor (it is important to get calibration values stored on the device).
    if (bmp180.begin() == 0)
        {// continue anyway but show valeus as "-99.9"
        Serial.println("BMP180 init FAIL!!");
        }
} // setup_

void loop()
{
Values values;
    if (!client.connected())
        {
        client.subscribe(topicSubscribe);
        reconnect();

        sprintf(topic, "%s%s", "/v1.6/devices/", DEVICE_LABEL);
        sprintf(payload, "%s", ""); // Cleans the payload
        sprintf(payload, "{\"%s\":", VARIABLE_LABEL); // Adds the variable label

        values = read_bmp180();
        publish(values);
        }
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
        values.temperature = T;
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
        values.pressure = P;
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

void reconnect()
{
    // Loop until we're reconnected
    while (!client.connected())
        {
        Serial.println("Attempting MQTT connection to: ");
        Serial.print(MQTT_SERVER);
        Serial.print("\n");
        // Attemp to connect
        if (client.connect(MQTT_CLIENT_NAME, TOKEN, ""))
            {
            Serial.println("Connected");
            client.subscribe(topicSubscribe);
            }
        else
            {
            Serial.print("Failed, rc=");
            Serial.print(client.state());
            Serial.print("\n");
            delay(RECONNECT_DELAY);
            }
        }
} // reconnect

void callback(char* topic, byte* payload, unsigned int length)
{
char p[length + 1];
    memcpy(p, payload, length);
    p[length] = NULL;
    String message(p);
    if (message == "0")
        {
        digitalWrite(intLed, HIGH);
        }
    else
        {
        digitalWrite(intLed, LOW);
        }
    Serial.write(payload, length);
    Serial.println();
} //callback

void publish(Values values)
{
    // ************ publish Temperature **********************
    float temperature = values.temperature;
    Serial.print("Temperature: ");
    Serial.println(temperature);
    Serial.print(" °C");
    /* 4 is minimum width (xx.x), 1 is precision; float value is copied onto str_sensor*/
    dtostrf(temperature, 4, 1, str_sensor);
    sprintf(payload, "%s {\"value\": %s}}", payload, str_sensor); // Adds the value
    //Serial.println("Publishing data to Ubidots Cloud");
    Serial.println("Publishing temperature to local mosquitto server on RPI3");
    client.publish(topic, payload);
    client.loop();
    //delay(250);

    // ************ publish Barometer **********************
    float barometer = values.pressure;
    Serial.print("Barometer: ");
    Serial.println(barometer);
    Serial.print("mbar");
    /* 7 is minimum width (xxxx.x), 1 is precision; float value is copied onto str_sensor*/
    dtostrf(barometer, 6, 1, str_sensor);
    sprintf(payload, "%s {\"value\": %s}}", payload, str_sensor); // Adds the value
    //Serial.println("Publishing data to Ubidots Cloud");
    Serial.println("Publishing barometer to local mosquitto server on RPI3");
    client.publish(topic, payload);
    client.loop();
    delay(PUBLISH_INTERVAL); // delay to next publish
} // publish
