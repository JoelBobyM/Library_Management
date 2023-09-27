#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define PN532_SCK  (14) //D5
#define PN532_MISO (12) //D6
#define PN532_MOSI (13) //D7
#define PN532_SS   (2)  //D4

#define RED_LED (16) //D0
#define BLUE_LED (5) //D1
#define YLW_LED (4) //D2

#ifndef STASSID
#define STASSID "Redmi"
#define STAPSK "uxny0984"
#endif

String serverName = "http://192.168.95.63:8000";

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

// Function to convert a byte array to a hexadecimal string
String byteArrayToHexString(uint8_t* byteArray, uint8_t length) 
{
  String hexString = "";
  for (int i = 0; i < length; i++) 
  {
    if (byteArray[i] < 16) 
    {
      hexString += "0"; // Add leading zero for single-digit values
    }
    hexString += String(byteArray[i], HEX);
  }
  hexString.toUpperCase();
  return hexString;
}

void setup()
{
  serverName += "/iot-input";

  pinMode(RED_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(YLW_LED, OUTPUT);

  Serial.begin(115200);
  Serial.flush();
  Serial.println("\n");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) 
  {
    digitalWrite(BLUE_LED,HIGH);
    delay(2000);
    digitalWrite(BLUE_LED,LOW);
    Serial.println("Didn't find PN53x board");
    while (1);
  }

  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);

  WiFi.begin(STASSID, STAPSK);
  Serial.print("\nWaiting for Wi-Fi ");
  while (WiFi.status() != WL_CONNECTED) 
  {
    digitalWrite(YLW_LED,HIGH);
    delay(500);
    Serial.print(".");
    digitalWrite(YLW_LED,LOW);
    delay(500);
  }
  Serial.println("\nWiFi connection Successful");
  Serial.print("The IP Address of ESP8266 Module is: ");
  Serial.println(WiFi.localIP());// Print the IP address

  nfc.SAMConfig();
  Serial.println("\nWaiting for an NFC card ...\n");
}

void loop() 
{

  uint8_t success, succ;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength; 

  StaticJsonDocument<200> jsonDoc;
  String jsonData;

  digitalWrite(RED_LED,HIGH);

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
  if (success) 
  {
    digitalWrite(RED_LED,LOW);
    digitalWrite(BLUE_LED,HIGH);

    Serial.println("Found 1st NFC card!");
    Serial.print("UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("UID Value: ");
    nfc.PrintHex(uid, uidLength);
    Serial.println("");

    jsonDoc["s_data"] = byteArrayToHexString(uid, uidLength);

    delay(1000);
    
    succ = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
    if (succ) 
    {
      digitalWrite(BLUE_LED,LOW);
      digitalWrite(YLW_LED,HIGH);
      Serial.println("Found 2nd NFC card!");
      Serial.print("UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
      Serial.print("UID Value: ");
      nfc.PrintHex(uid, uidLength);
      Serial.println("");
      delay(1000);
      digitalWrite(YLW_LED,LOW);

      jsonDoc["b_data"] = byteArrayToHexString(uid, uidLength);
      
      if(WiFi.status()== WL_CONNECTED)
      {
        WiFiClient client;
        HTTPClient http;

        http.begin(client, serverName);
        serializeJson(jsonDoc, jsonData);
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Bypass-Tunnel-Reminder", "cmps e_lib");


        int httpCode = http.POST(jsonData);
        const String& payload = http.getString();

        Serial.println(jsonData); 
        Serial.print("HTTP Response Code : "); Serial.println(httpCode);
        Serial.print("HTTP Response Body :"); Serial.println(payload);

        if(httpCode == HTTP_CODE_OK)
        {
          Serial.println("Authentication Success");
          for(int i=0;i<5;i++)
          {
            digitalWrite(BLUE_LED,HIGH);
            delay(200);
            digitalWrite(BLUE_LED,LOW);
            delay(200);
            digitalWrite(YLW_LED,HIGH);
            delay(200);
            digitalWrite(YLW_LED,LOW);
            delay(200);
          }
        }
        else
        {
          Serial.println("Authentication Failure");
          for(int i=0;i<5;i++)
          {
            digitalWrite(BLUE_LED,HIGH);
            delay(200);
            digitalWrite(BLUE_LED,LOW);
            delay(200);
            digitalWrite(RED_LED,HIGH);
            delay(200);
            digitalWrite(RED_LED,LOW);
            delay(200);
          }
        }
        http.end();
      }
    }
  }
}