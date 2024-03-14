#include <WiFi.h>
#include <FS.h>
#include <SPIFFS.h>
#include <SimpleFTPServer.h>
#include <sys/stat.h>
#include "filesystem.h"
#include "ftp.h"

const char *ssid = "YOUR_WIFI_AP";
const char *password = "YOUR_WIFI_PW";

#define BAUDRATE 115200

#define ADDRESS_CNT_CLEAR_SIO2    22 // Address counter clear, HX-output
#define SHIFT_REG_CLEAR_SIO4      23 // Shift register clear, HX-output
#define SERIAL_DATA_M11           26 // HX-input, Shift register output
#define SHIFT_CLOCK_M02           27 // Shift register clock, HX-output
#define ADDRESS_COUNTER_M01       25 // Address Counter input, HX-output

void initGPIOs() {
  pinMode(ADDRESS_CNT_CLEAR_SIO2, INPUT);
  pinMode(SHIFT_REG_CLEAR_SIO4,   INPUT);
  pinMode(SHIFT_CLOCK_M02,        INPUT);
  pinMode(ADDRESS_COUNTER_M01,    INPUT);
  pinMode(SERIAL_DATA_M11,        OUTPUT);
}


File     file;
bool     next_bit = false;
uint8_t  rom_buffer[8196];
uint8_t  next_byte       = 0;
uint8_t  shift_counter   = 0;
uint16_t address_counter = 0;

void IRAM_ATTR INT_ADDRESS_COUNTER_CLEAR() {
  address_counter = 0;
}

void IRAM_ATTR INT_SHIFT_REGISTER_CLEAR() {
  next_byte = 0;
}

void IRAM_ATTR INT_INCREMENT_ADDRESS() {
  address_counter++;
  next_byte = rom_buffer[address_counter];
}

void IRAM_ATTR INT_GET_SERIAL_DATA() {
  next_bit = bitRead(next_byte, 7-shift_counter);
  shift_counter++; if (shift_counter>7) shift_counter = 0;
  digitalWrite(SERIAL_DATA_M11, next_bit);
}

void setup(void) {

  Serial.begin(BAUDRATE);
  initGPIOs();

  initFS();
  listDir(SPIFFS, "/", 0);
  file = SPIFFS.open("/pac0.rom");
  uint8_t i = 0;
  while (file.available()){ rom_buffer[i] = file.read(); i++; } file.close();

  attachInterrupt(ADDRESS_COUNTER_M01,    INT_INCREMENT_ADDRESS,      FALLING);
  attachInterrupt(SHIFT_CLOCK_M02,        INT_GET_SERIAL_DATA,        RISING);
  attachInterrupt(ADDRESS_CNT_CLEAR_SIO2, INT_ADDRESS_COUNTER_CLEAR,  RISING);
  attachInterrupt(SHIFT_REG_CLEAR_SIO4,   INT_SHIFT_REGISTER_CLEAR,   FALLING);

  initFTP(ssid, password);
}


void loop(void) {
  ftpSrv.handleFTP();
}
