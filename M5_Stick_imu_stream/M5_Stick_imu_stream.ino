#include <M5StickC.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include "AXP192.h"
#include <M5GFX.h>
//M5GFX display;
#include "MLab_MPU6886.h"
#include "MLab_packet.h"
#include "wifi_conf.h"


MLab_packet dataStreamframe;

MLab_MPU6886 imu;
const int INTERNAL_SAMPLE_RATE = 1000;

const uint16_t tcpServerPort = 8000;
AsyncServer *dataStreamTcpServer = NULL;
AsyncClient *dataStreamClient = NULL;// supportsingle client for now

bool data_stream_flag = false;
uint16_t stream_pack_idx = 0;

void setup() {
  M5.begin();
  imu.Init();
  Serial.begin(115200);
  uint8_t buf[1];

  //imu.I2C_Read_NBytes(MPU6886_ADDRESS, MPU6886_SMPLRT_DIV, 1, buf);
  //SAMPLE_RATE = INTERNAL_SAMPLE_RATE / (1 + SMPLRT_DIV)
  //(1 + SMPLRT_DIV) = INTERNAL_SAMPLE_RATE / SAMPLE_RATE
  //SMPLRT_DIV = (INTERNAL_SAMPLE_RATE / SAMPLE_RATE) - 1

  int SAMPLE_RATE = 250;
  uint8_t SMPLRT_DIV = (INTERNAL_SAMPLE_RATE / SAMPLE_RATE) - 1;
  buf[0] = SMPLRT_DIV;

  imu.I2C_Write_NBytes(MPU6886_ADDRESS, MPU6886_SMPLRT_DIV, 1, buf);
  M5.Axp.EnableCoulombcounter();  // Enable Coulomb counter.  启用库仑计数器
  M5.Lcd.begin();
  M5.Lcd.setRotation(3);

  if (WIFI_MODE == WIFI_STA) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PSWD);
    Serial.print("Connecting to: ");
    Serial.println(WIFI_SSID);

  }
  else if (WIFI_MODE == WIFI_AP) {
    const char* ap_ssid     = "mini-4WD_IMU";
    const char* ap_password = "123456789";
    WiFi.mode(WIFI_AP);
    WiFi.begin(ap_ssid, ap_password);
  }

  dataStreamTcpServer = new AsyncServer(tcpServerPort); // start listening on tcpServerPort
  //dynamic programming, dataStreamTcpServer is dynamics variable, use "new" to allocate varaible in memory
  dataStreamTcpServer->onClient(&handleTcpNewClient, dataStreamTcpServer);
  dataStreamTcpServer->begin();
  MLab_packet_init();

}

void loop() {
  float temp = 0;
  static unsigned long prev_us = micros();
  static unsigned long prev_interval_ms = millis();
  uint8_t buf[1];
  //imu.I2C_Read_NBytes(MPU6886_ADDRESS, MPU6886_INT_STATUS, 1, buf);
  if (imu.available()) {
    Serial.println(micros() - prev_us);
    prev_us = micros();
    imu.readAll();
    stream_pack_idx++;
    //Serial.print('\t');
    //Serial.println(imu.raw_accZ());
    if (data_stream_flag) {
      tcp_stream() ;
    }
  }
  if (millis() - prev_interval_ms > 2000) {
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setTextColor(WHITE);
    prev_interval_ms = millis();
    M5.Lcd.setCursor(0, 0, 1);
    M5.Lcd.printf("AXP Temp: % .1fC \r\n", M5.Axp.GetTempInAXP192());
    M5.Lcd.printf("Bat:% .2fV % .2fmA\r\n", M5.Axp.GetBatVoltage(), M5.Axp.GetBatCurrent());
    int wifi_status = WiFi.status();
    if (wifi_status == WL_CONNECTED) {
      M5.Lcd.setTextColor(GREEN);
      M5.Lcd.printf("WiFi connected\r\n");
      M5.Lcd.setTextColor(WHITE);
      M5.Lcd.printf("IP:%s\r\n", WiFi.localIP().toString().c_str());

    }
    else if (wifi_status == WL_NO_SSID_AVAIL) {
      M5.Lcd.setTextColor(RED);
      M5.Lcd.printf("SSID not found");
    }
    else {
      M5.Lcd.setTextColor(RED);
      M5.Lcd.printf("WiFi not connected");
    }
    if (data_stream_flag) {

      M5.Lcd.setTextColor(GREEN);
      M5.Lcd.printf("Stream : %s\r\n", dataStreamClient->remoteIP().toString().c_str());
    }

  }

}
void tcp_stream() {
  dataStreamframe.init();
  dataStreamframe.pack_instruction(0x04);

  //
  dataStreamframe.addDataToPack(stream_pack_idx);
  dataStreamframe.addDataToPack(imu.raw_accX());
  dataStreamframe.addDataToPack(imu.raw_accY());
  dataStreamframe.addDataToPack(imu.raw_accZ());
  dataStreamframe.addDataToPack(imu.raw_gyroX());
  dataStreamframe.addDataToPack(imu.raw_gyroY());
  dataStreamframe.addDataToPack(imu.raw_gyroZ());

  dataStreamframe.make_packet();


  if (dataStreamClient->space() > dataStreamframe.tx_len() && dataStreamClient->canSend())
  {
    dataStreamClient->write((const char*)dataStreamframe.tx_buf, dataStreamframe.tx_len());


    //dataStreamClient->send();

  }
  // send the data to the client

}
