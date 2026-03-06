#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <EMailSender.h>
#include <ESP8266WiFi.h>

#define BUTTON_PIN 5  // Try GPIO 4 if D1 doesn't work
#define RXPin 14  
#define TXPin 12  
#define GPSBaud 9600

const char* ssid = "iphone";
const char* password = "111111111";

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);
EMailSender emailSend("womensafetyproject22@gmail.com", "zyev ydoz hqgx cemt");

bool emailSent = false;  // Track if an email has been sent

void setup() {
    Serial.begin(115200);
    ss.begin(GPSBaud);
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected!");
}

void loop() {
    while (ss.available()) {
        gps.encode(ss.read());
    }

    if (digitalRead(BUTTON_PIN) == LOW && !emailSent) {  
        Serial.println("Button Pressed! Sending GPS Email...");
        emailSent = true;  // Prevent multiple emails
        sendEmail(gps.location.lat(), gps.location.lng());
    }
    
    // Wait for the button to be released before allowing another press
    if (digitalRead(BUTTON_PIN) == HIGH) {  
        emailSent = false;
    }
}

void sendEmail(double latitude, double longitude) {
    if (!gps.location.isValid()) {
        Serial.println("GPS Signal Not Found! Email not sent.");
        return;
    }

    String googleMapsLink = "https://maps.google.com/?q=" + String(latitude, 6) + "," + String(longitude, 6);
    String messageBody = "🚨 EMERGENCY ALERT 🚨\n\n"
                         "Live Location:\n" + googleMapsLink + "\n\n"
                         "Stay Safe!";

    EMailSender::EMailMessage message;
    message.subject = "Emergency Alert!";
    message.message = messageBody;

    EMailSender::Response resp = emailSend.send("mbadrinath5222@gmail.com", message);

    Serial.println("Sending status: ");
    Serial.println(resp.status);
    Serial.println(resp.code);
    Serial.println(resp.desc);

    /*if (resp.code.toInt() != 200) {
        Serial.println("Email failed! Retrying in 30s...");
        delay(30000);
        sendEmail(latitude, longitude);
    }*/
}
