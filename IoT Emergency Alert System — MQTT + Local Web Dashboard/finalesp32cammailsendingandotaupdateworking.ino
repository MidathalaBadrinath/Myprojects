#include "esp_camera.h"
#include "SPI.h"
#include "driver/rtc_io.h"
#include <ESP_Mail_Client.h>
#include <FS.h>
#include <WiFi.h>
#include <WebServer.h>
#include <EEPROM.h>

// REPLACE WITH YOUR NETWORK CREDENTIALS
const char* ssid = "iphone";
const char* password = "111111111";

// To send Email using Gmail use port 465 (SSL) and SMTP Server smtp.gmail.com
// You need to create an email app password
#define emailSenderAccount    "womensafetyproject22@gmail.com"
#define emailSenderPassword   "zyev ydoz hqgx cemt"
#define smtpServer            "smtp.gmail.com"
#define smtpServerPort        465

#define emailSubject          "🚨 EMERGENCY ALERT: Suspicious Activity Detected 🚨"

#define BUTTON_PIN 13  // GPIO pin where the safety button is connected

// EEPROM settings
#define EEPROM_SIZE 64
#define EMAIL_ADDR_OFFSET 0

// Web server
WebServer server(80);

// Global variable to store recipient email
String recipientEmail = "";

#define CAMERA_MODEL_AI_THINKER

#if defined(CAMERA_MODEL_AI_THINKER)
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#else
  #error "Camera model not selected"
#endif

/* The SMTP Session object used for Email sending */
SMTPSession smtp;

/* Callback function to get the Email sending status */
void smtpCallback(SMTP_Status status);

// Photo File Name to save in LittleFS
#define FILE_PHOTO "photo.jpg"
#define FILE_PHOTO_PATH "/photo.jpg"

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  Serial.println();

  // Initialize EEPROM
  EEPROM.begin(EEPROM_SIZE);
  loadRecipientEmail();

  // Initialize the safety button pin as an input
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  
  // Print ESP32 Local IP Address
  Serial.print("IP Address: http://");
  Serial.println(WiFi.localIP());

  // Init filesystem
  ESP_MAIL_DEFAULT_FLASH_FS.begin();
   
  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Start web server
  server.on("/", handleRoot);
  server.on("/update", handleUpdate);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  // Handle web server requests
  server.handleClient();

  // Check if the safety button is pressed
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(100);  // Debounce delay
    if (digitalRead(BUTTON_PIN) == LOW) {
      Serial.println("🚨 Safety Button Pressed! Sending Emergency Alert...");
      capturePhotoSaveLittleFS();
      sendPhoto();
      delay(1000);  // Wait for a second to avoid multiple triggers
    }
  }
}

// Load recipient email from EEPROM
void loadRecipientEmail() {
  recipientEmail = "";
  for (int i = 0; i < EEPROM_SIZE; i++) {
    char c = EEPROM.read(EMAIL_ADDR_OFFSET + i);
    if (c == 0) break;
    recipientEmail += c;
  }
  Serial.println("Loaded recipient email: " + recipientEmail);
}

// Save recipient email to EEPROM
void saveRecipientEmail(String email) {
  for (int i = 0; i < email.length(); i++) {
    EEPROM.write(EMAIL_ADDR_OFFSET + i, email[i]);
  }
  EEPROM.write(EMAIL_ADDR_OFFSET + email.length(), 0); // Null-terminate
  EEPROM.commit();
  Serial.println("Saved recipient email: " + email);
}

// Handle root URL
void handleRoot() {
    String html = "<!DOCTYPE html>"
                  "<html lang='en'>"
                  "<head>"
                  "<meta charset='UTF-8'>"
                  "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                  "<title>Women Safety - Email Update</title>"
                  "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>"
                  "<script src='https://cdn.jsdelivr.net/npm/sweetalert2@11'></script>"
                  "<style>"
                  "body { font-family: Arial, sans-serif; transition: 0.5s ease-in-out; }"
                  ".container { max-width: 500px; margin-top: 50px; padding: 20px; background: white; "
                  "box-shadow: 0px 0px 15px rgba(0,0,0,0.2); border-radius: 10px; animation: fadeIn 1s; }"
                  "@keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }"
                  ".btn-update { width: 100%; animation: pulse 1.5s infinite; }"
                  "@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }"
                  "input { transition: 0.3s; }"
                  "input:focus { border-color: #007bff; box-shadow: 0 0 8px rgba(0, 123, 255, 0.5); }"
                  "@media (prefers-color-scheme: dark) { body { background: #222; color: white; } .container { background: #333; color: white; } input { background: #444; color: white; border-color: #007bff; } }"
                  "</style>"
                  "</head>"
                  "<body>"
                  "<div class='container text-center'>"
                  "<h1 class='text-primary'><i class='bi bi-envelope'></i> Update Emergency Email</h1>"
                  "<form id='emailForm' action='/update' method='POST'>"
                  "<div class='mb-3'>"
                  "<label class='form-label'>New Email Address:</label>"
                  "<input type='email' class='form-control' id='emailInput' name='email' value='" + recipientEmail + "' required>"
                  "</div>"
                  "<button type='submit' class='btn btn-primary btn-update'>Update Email</button>"
                  "</form>"
                  "<br><p><strong>Current Email:</strong> <span id='currentEmail'>" + recipientEmail + "</span></p>"
                  "</div>"
                  "<script>"
                  "document.getElementById('emailForm').addEventListener('submit', function(event) {"
                  " event.preventDefault();"
                  " let email = document.getElementById('emailInput').value;"
                  " if (!email.includes('@') || !email.includes('.')) {"
                  " Swal.fire('⚠️ Invalid Email!', 'Please enter a valid email address.', 'error');"
                  " return;"
                  " }"
                  " fetch('/update', { method: 'POST', body: new URLSearchParams({ 'email': email }) })"
                  " .then(response => response.text())"
                  " .then(data => {"
                  " Swal.fire('✅ Success!', 'Email updated to: ' + email, 'success');"
                  " document.getElementById('currentEmail').innerText = email;"
                  " })"
                  " .catch(error => Swal.fire('❌ Error!', 'Something went wrong!', 'error'));"
                  "});"
                  "</script>"
                  "</body></html>";
    server.send(200, "text/html", html);
}


// Handle email update
void handleUpdate() {
  if (server.hasArg("email")) {
    String newEmail = server.arg("email");
    saveRecipientEmail(newEmail);
    recipientEmail = newEmail;
    server.send(200, "text/plain", "Email updated to: " + newEmail);
  } else {
    server.send(400, "text/plain", "Error: No email provided");
  }
}

// Capture Photo and Save it to LittleFS
void capturePhotoSaveLittleFS() {
  camera_fb_t* fb = NULL;
  for (int i = 0; i < 3; i++) {
    fb = esp_camera_fb_get();
    esp_camera_fb_return(fb);
    fb = NULL;
  }
    
  fb = esp_camera_fb_get();  
  if(!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    ESP.restart();
  }  

  File file = LittleFS.open(FILE_PHOTO_PATH, FILE_WRITE);
  if (!file) {
    Serial.println("Failed to open file in writing mode");
  } else {
    file.write(fb->buf, fb->len);
    Serial.print("The picture has been saved in ");
    Serial.print(FILE_PHOTO_PATH);
    Serial.print(" - Size: ");
    Serial.print(fb->len);
    Serial.println(" bytes");
  }
  file.close();
  esp_camera_fb_return(fb);
}

// Send Photo via Email
void sendPhoto() {
  smtp.debug(1);
  smtp.callback(smtpCallback);

  Session_Config config;
  config.time.ntp_server = F("pool.ntp.org,time.nist.gov");
  config.time.gmt_offset = 0;
  config.time.day_light_offset = 1;
  config.server.host_name = smtpServer;
  config.server.port = smtpServerPort;
  config.login.email = emailSenderAccount;
  config.login.password = emailSenderPassword;
  config.login.user_domain = "";

  SMTP_Message message;
  message.enable.chunking = true;
  message.sender.name = "Women Safety Device";
  message.sender.email = emailSenderAccount;
  message.subject = emailSubject;
  message.addRecipient("Emergency Contact", recipientEmail);

  String htmlMsg = "<h2>🚨 EMERGENCY ALERT 🚨</h2>";
  htmlMsg += "<p>A suspicious activity or potential danger has been detected by the Women Safety Device.</p>";
  htmlMsg += "<p>Please check the attached image for details and take immediate action.</p>";
  htmlMsg += "<p><strong>Device IP Address:</strong> " + WiFi.localIP().toString() + "</p>";
  //htmlMsg += "<p><strong>Time:</strong> " + String(__TIME__) + "</p>";

  message.html.content = htmlMsg.c_str();
  message.html.charSet = "utf-8";
  message.html.transfer_encoding = Content_Transfer_Encoding::enc_qp;

  SMTP_Attachment att;
  att.descr.filename = FILE_PHOTO;
  att.descr.mime = "image/jpeg"; 
  att.file.path = FILE_PHOTO_PATH;
  att.file.storage_type = esp_mail_file_storage_type_flash;
  att.descr.transfer_encoding = Content_Transfer_Encoding::enc_base64;
  message.addAttachment(att);

  if (!smtp.connect(&config)) return;
  if (!MailClient.sendMail(&smtp, &message, true))
    Serial.println("Error sending Email, " + smtp.errorReason());
}

// Callback function to get the Email sending status
void smtpCallback(SMTP_Status status){
  Serial.println(status.info());
  if (status.success()) {
    Serial.println("Message sent successfully!");
  }
}