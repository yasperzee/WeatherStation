  /************************ nodemcu-weather-mqtt.ino ***************************
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

/* ---------------- Version history --------------------------------------------
# TODO: sleep
# TODO: Support for BSE280 sensor w/ temperature, humidity & pressure.

    Version 0.2     Yasperzee   3'19
                    topic levels defined
                    koti/oh/temperature
                    koti/oh/humidity

    Version 0.1     Yasperzee   2'19
                    mqtt client functionality tested.


------------------------------------------------------------------------------*/

// includes
#include "ssid.h"  // SSID and PASS strings for local network
#include <ESP8266WiFi.h>
#include <SFE_BMP180.h>
#include <PubSubClient.h>

// defines
// #define ALTITUDE 119.0 // Altitude of Tampere-Pirkkala airport, Finland. In meters
#define ALTITUDE 129.0 // Altitude of Kalkunvuori, Tampere Finland. In meters

//#define MQTT_SERVER     "192.168.10.52" // Local Rpi3 with mosquitto
#define MQTT_SERVER         "192.168.10.33" // Local W530 with mosquitto
#define MQTT_DEVICE_LABEL   "BMP180_01" // Assing the device label
#define MQTT_CLIENT_ID      "ESP01_01"    // MQTT client Name, please enter your own 8-12 alphanumeric character ASCII string;
                                        // it should be a random and unique ascii string and different from all other devices

// topic level definitions
#define TOPIC_WILDCARD_SINGLE "+"
#define TOPIC_WILDCARD_MULTI  "#"

#define TOPIC_LOCATION "koti"

//#define TOPIC_ROOM "mh-1"   // makkari 1
//#define TOPIC_ROOM "mh-2"   // makkari 2
//#define TOPIC_ROOM "mh-3"   // makkari 3
//#define TOPIC_ROOM "et"     // eteinen
//#define TOPIC_ROOM "kt"     // keittiö
#define TOPIC_ROOM "oh"     // olkkari
//#define TOPIC_ROOM "ph"     // kylppäri
//#define TOPIC_ROOM "wc"     // vessa
//#define TOPIC_ROOM "ulkoilma"

#define TOPIC_TEMP      "temperature"
#define TOPIC_HUMID     "humidity"
#define TOPIC_BARO      "barometer"

// constants
const int PUBLISH_INTERVAL  = 5000; // intervall to publish
const int RECONNECT_DELAY   = 2500; // Try to reconnect mqtt server
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
    double temperature;
    double pressure;
    };

// Function declarations
Values read_bmp180(void);
int mqtt_connect();
int mqtt_subscribe(char topicSubscribe[]);
void mqtt_publish(Values);
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
        delay(500);
        Serial.print(".");
        }
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    client.setServer(MQTT_SERVER, 1883);
    client.setCallback(callback);

    // BEST PRACTICE: Do not use leading '/'
    //sprintf(topicSubscribe, "%s/%s/%s", TOPIC_LOCATION, TOPIC_ROOM, TOPIC_TEMP );
/* DEBUG
    Serial.print("topicSubscribe: ");
    Serial.print(topicSubscribe);
    Serial.println("");
DEBUG */
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
int state =0;
    state = mqtt_connect();

    //mqtt_subscribe(topicSubscribe);

    values = read_bmp180();
    mqtt_publish(values);
    delay(PUBLISH_INTERVAL); // delay to next publish

} // loop

int mqtt_connect()
{
int state = 0;
    if (!client.connected())
        {
        if (client.connect(MQTT_CLIENT_ID))
            {
            Serial.print("\n");
            Serial.println("MQTT re-connected.");
            //Serial.println("topicSubdsribe: ");
            //Serial.print(topicSubscribe);
            //Serial.print("\n");
            }
        else
            {
            Serial.print("\n");
            Serial.print("MQTT re-connection FAIL! ");
            //delay(RECONNECT_DELAY);
            }
        }
    else
        {
        Serial.println("");
        Serial.println("MQTT already connected.");
        }
        state = client.state();
        return(state);
} // mqtt_connect

int mqtt_subscribe(char topicSubscribe[])
{
    Serial.print("mqtt_subdsribe: ");
    Serial.print(topicSubscribe);
    Serial.print("\n");
    // BEST PRACTICE: Do not use leading '/'
    //sprintf(topicSubscribe, "%s/%s/%s", TOPIC_LOCATION, TOPIC_ROOM, TOPIC_WILDCARD_MULTI );
    //client.subscribe(topicSubscribe);
    // do something with response --> callback
}

void mqtt_publish(Values values)
{
    // ************ publish Temperature **********************
    float temperature = values.temperature;
    //Serial.print("Temperature: ");
    //Serial.print(temperature);
    //Serial.println(" °C");
    /* 4 is minimum width (xx.x), 1 is precision; float value is copied onto str_sensor*/
    dtostrf(temperature, 4, 1, str_sensor);
    sprintf(payload, "%s", ""); // Cleans the payload
    // BEST PRACTICE: Do not use leading '/'
    sprintf(topic, "%s/%s/%s", TOPIC_LOCATION, TOPIC_ROOM, TOPIC_TEMP );
    sprintf(payload, "{\"temperature\": %s}", str_sensor); // Adds the value
    //sprintf(payload, "{%s {\"temperature\": %s}}", payload, str_sensor); // Adds the value
    Serial.println("");
    Serial.println("Publishing temperature to local mosquitto server");
    Serial.print("topic: ");
    Serial.println(topic);
    Serial.print("payload: ");
    Serial.print(payload);
    Serial.println("");
    client.publish(topic, payload);

    // ************ publish Barometer **********************
    float barometer = values.pressure;
    //Serial.print("Barometer: ");
    //Serial.print(barometer);
    //Serial.println(" mbar");
    /* 7 is minimum width (xxxx.x), 1 is precision; float value is copied onto str_sensor*/
    dtostrf(barometer, 6, 1, str_sensor);
    sprintf(payload, "%s", ""); // Cleans the payload
    // BEST PRACTICE: Do not use leading '/'
    sprintf(topic, "%s/%s/%s", TOPIC_LOCATION, TOPIC_ROOM, TOPIC_BARO );
    sprintf(payload, "{\"barometer\": %s}", str_sensor); // Adds the value
    Serial.println("");
    Serial.println("Publishing barometer to local mosquitto server");
    Serial.print("topic: ");
    Serial.println(topic);
    Serial.print("payload: ");
    Serial.print(payload);
    Serial.println("");
    client.publish(topic, payload);
    client.loop();
} // publish

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
    Serial.print("callback: ");
    Serial.write(payload, length);
    Serial.println();
} //callback
