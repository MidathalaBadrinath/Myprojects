#include <WiFi.h>
#include <DHT.h>

// Replace with your network credentials
const char* ssid = "YourSSID";
const char* password = "YourPassword";

// Create an instance of the DHT sensor
DHT dht(DHT_PIN, DHT_TYPE);

const int DHT_PIN = 4; // GPIO pin where DHT sensor is connected

void setup() {
  Serial.begin(115200);
  pinMode(DHT_PIN, INPUT);
  dht.begin();
  connectToWiFi();
}

void connectToWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  float humidity = dht.readHumidity();
  float moisture = analogRead(A0); // Replace A0 with your moisture sensor pin
  
  if (isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor");
    return;
  }

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("%, Moisture: ");
  Serial.println(moisture);
  
  // Send data to Raspberry Pi via HTTP POST request or MQTT
  // You need to implement the sending logic here
  // You can use libraries like HTTPClient or PubSubClient for MQTT

  delay(5000); // Adjust the sending interval as needed
}