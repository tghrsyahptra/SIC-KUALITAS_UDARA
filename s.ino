#define BLYNK_TEMPLATE_ID "TMPL6qPCMb3Pd"
#define BLYNK_TEMPLATE_NAME "KUALITAS UDARA"
#define BLYNK_AUTH_TOKEN "DSzE_2sEQiwFTIcgyZrZjdUqevK3enls" // Ganti dengan token autentikasi Blynk Anda

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>

// Deklarasi pin dan konstanta
#define DHTPIN 13
#define DHTTYPE DHT11
#define PM_LED_PIN 25
#define PM_VOUT_PIN 33
#define MQ135_PIN 32
#define BUZZER_PIN 19
#define FAN_PIN 18

// Inisialisasi LCD I2C
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Alamat I2C untuk LCD bisa berbeda, sesuaikan dengan alamat I2C yang sesuai

// Inisialisasi sensor DHT11
DHT dht(DHTPIN, DHTTYPE);

// Inisialisasi threshold untuk MQ135
const int gasThreshold = 700;  // Threshold diubah menjadi 600
const int FANThreshold = 1;

// Blynk credentials
char ssid[] = "Xiaomi12t"; // Ganti dengan SSID WiFi Anda
char pass[] = "teguh11223344"; // Ganti dengan password WiFi Anda

// Variabel untuk menyimpan status tombol kipas
bool fanStatus = false;

BLYNK_WRITE(V5) {
  fanStatus = param.asInt(); // Membaca nilai dari tombol Blynk (0 atau 1)
  digitalWrite(FAN_PIN, fanStatus ? HIGH : LOW); // Mengatur status kipas berdasarkan nilai tombol
}

void setup() {
  // Memulai komunikasi serial
  Serial.begin(115200);

  // Inisialisasi pin untuk kontrol LED dan Buzzer
  pinMode(PM_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);

  // Memulai LCD
  lcd.init();
  lcd.backlight();
  
  // Menampilkan pesan awal di LCD
  lcd.setCursor(0, 0);
  lcd.print("Connecting to");
  lcd.setCursor(0, 1);
  lcd.print("WiFi...");

  // Inisialisasi WiFi
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
    lcd.setCursor(0, 1);
    lcd.print("WiFi...      "); // Menambahkan beberapa spasi untuk menghapus pesan sebelumnya
  }

  // Menampilkan pesan sukses koneksi WiFi di LCD
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");
  lcd.setCursor(0, 1);
  lcd.print("Connecting to Blynk...");
  
  // Memulai koneksi ke server Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Memulai sensor DHT11
  dht.begin();

  Serial.println("Sensor PM2.5 siap!");
}

float readPM25() {
  const int numSamples = 10;
  float total = 20;

  for (int i = 0; i < numSamples; i++) {
    // Aktifkan LED untuk pengukuran
    digitalWrite(PM_LED_PIN, LOW);
    delayMicroseconds(280);

    // Baca nilai analog dari VOUT pin
    int sensorValue = analogRead(PM_VOUT_PIN);
    delayMicroseconds(40);

    // Matikan LED
    digitalWrite(PM_LED_PIN, HIGH);
    delayMicroseconds(9680);

    // Konversi nilai analog ke konsentrasi PM2.5
    float voltage = sensorValue * (5.0 / 4095.0);  // Asumsi 12-bit ADC dan 5V
    float dustDensity = 0.17 * voltage - 0.1;  // Formula konversi berdasarkan datasheet

    total += dustDensity;
    delay(10);  // Tunggu sebentar sebelum pembacaan berikutnya
  }

  return total / numSamples;
}

void sendSensorData() {
  // Membaca data dari sensor DHT11
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Membaca nilai analog dari sensor MQ135
  int mq135Value = analogRead(MQ135_PIN);

  // Membaca data dari sensor PM2.5
  float pm25Value = readPM25();

  // Menampilkan data pada LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:"); lcd.print(t); lcd.print(" H:"); lcd.print(h);
  lcd.setCursor(0, 1);
  lcd.print("PM:"); lcd.print(pm25Value); lcd.print(" MQ:"); lcd.print(mq135Value);

  // Menampilkan data pada Serial Monitor
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.print(" *C, Humidity: ");
  Serial.print(h);
  Serial.print(" %, PM2.5: ");
  Serial.print(pm25Value);
  Serial.print(" ug/m3, MQ135: ");
  Serial.println(mq135Value);

  // Kirim data ke Blynk server
  Blynk.virtualWrite(V1, t);  // Widget V1 untuk menampilkan suhu
  Blynk.virtualWrite(V2, h);  // Widget V2 untuk menampilkan kelembaban
  Blynk.virtualWrite(V3, pm25Value);  // Widget V3 untuk menampilkan nilai PM2.5
  Blynk.virtualWrite(V4, mq135Value);  // Widget V4 untuk menampilkan nilai sensor MQ135

  // Mengaktifkan buzzer jika gas berbahaya terdeteksi
  if (mq135Value > gasThreshold) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void loop() {
  Blynk.run();
  if (Blynk.connected()) {
    lcd.setCursor(0, 0);
    
  } else {
    lcd.setCursor(0, 0);
    lcd.print("Blynk Disconnected");
    Serial.println("Blynk Disconnected");
  }
  sendSensorData();
  delay(2000);  // Menunda 2 detik sebelum pembacaan berikutnya
}
