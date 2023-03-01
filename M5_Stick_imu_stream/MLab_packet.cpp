#include "MLab_packet.h"
uint8_t crc8_table[256];
void MLab_packet_init(){
  crc8_init();
}

uint8_t MLab_packet::tx_len() {
  return payload_len + head_offset + 1; // add 1-byte of CRC
}


void MLab_packet::init() {
  pack_idx = 0;
  payload_len = 0;
  pack_instruction(0);
}
void MLab_packet::pack_header() {
  tx_buf[0] = 0xFF;
  tx_buf[1] = 0xFF;
}
void MLab_packet::pack_instruction(uint8_t ins) {
  tx_buf[2] = ins;
}
void MLab_packet::pack_len() {
  tx_buf[3] = payload_len + 1;//included COBD over head
}
/*
  template<typename T>
  void MLab_packet::addDataToPack(T var) {
  memcpy(tx_buf + head_offset + payload_len, reinterpret_cast<const byte*>(&var), sizeof(var));
  payload_len += sizeof(var);
  }
*/
void MLab_packet::printPayload() {
  Serial.print("payload\'s data: ");
  for (int i = 0; i < payload_len; i++) {
    Serial.print(tx_buf[head_offset + i], HEX);
    Serial.print(" ");
    if (i == payload_len - 1)Serial.println();
  }
}
void MLab_packet::printPacket() {
  Serial.print("packet\'s data: ");
  for (int i = 0; i < payload_len + head_offset + 1; i++) {
    Serial.print(tx_buf[i], HEX);
    Serial.print(" ");

  }
  Serial.println();
}
void MLab_packet::make_packet() {
  // Make packet and store in buffer.
  pack_header();
  pack_len();
  crc8();
  encodeCOBS();
}

void MLab_packet::crc8() {
  // add crc to packet
  uint8_t crc = 0;
  for (int i = 0; i < payload_len; i++) {
    crc = crc8_table[crc ^ tx_buf[i + head_offset]];
  }
  pack_crc = crc;
  tx_buf[payload_len + head_offset] = crc;

}

void MLab_packet::encodeCOBS() {
  //Serial.println("encodeCOBS");
  uint8_t codeValue = 1;

  int codeidx = -1;//shifted left from actual payload
  for (int i = 0; i < payload_len + 1; i++) { // payload_len+1 to include CRC (CRC might be 0xFF)
    uint8_t crr_byte = tx_buf[head_offset + i];
    if (crr_byte == COBS_DELIMITER) {
      tx_buf[head_offset + codeidx] = codeValue;
      codeValue = 1;
      codeidx = i;
    }
    else {
      codeValue++;
    }

  }
  // For final code
  tx_buf[head_offset + codeidx] = codeValue;
}

void MLab_packet::load_buf(uint8_t *src, size_t len) {
  memcpy(tx_buf, src, len);
}
bool MLab_packet::verify_header() {
  return tx_buf[0] == 0xFF && tx_buf[1] == 0xFF;
}
uint8_t MLab_packet::get_ins() {
  return tx_buf[2];

}
uint8_t MLab_packet::get_packlen() {
  return tx_buf[3];

}
bool MLab_packet::decodeCOBS(uint8_t *dst) {
  uint8_t packlen = get_packlen();
  uint8_t code_idx = 0;
  uint8_t cal_crc = 0;
  for (int i = 0; i < packlen + 1; i++) { //packlen +1 to include COBS over head

    uint8_t crr_byte =  tx_buf[head_offset + i - 1]; // shift back by 1 to include COBS over head
    //Serial.printf("iteration: %d, data = 0x%02x\r\n",i,crr_byte);
    if (i == code_idx) {
      //Serial.printf("found code at idx: %d\r\n", i);
      code_idx += crr_byte;
      //Serial.printf("code_idx shift to idx: %d\r\n", code_idx);
      if (i > 0) {
        dst[i - 1] = 0xFF;
        //Serial.printf("change dst[%d] to 0xFF\r\n", i - 1);
      }
    }
    else  if (i > 0) {
      dst[i - 1] = crr_byte;
      //Serial.printf("dst[%d] = 0x%02x\r\n", i - 1, crr_byte);

    }
    // For CRC check
    if (i > 0) {

      //Serial.printf("dst[%d] = 0x%02x\r\n", i - 1, crr_byte);
      if (i < packlen) { // calculate CRC
        cal_crc = crc8_table[cal_crc ^ dst[i - 1]];
        //Serial.printf("cal_CRC at %d = 0x%02x\r\n", i - 1, cal_crc);
      }
      else { // last byte is CRC from packet for verify.
        uint8_t pack_crc = dst[i - 1];
        Serial.printf("cal_CRC = 0x%02x, pack_crc 0x%02x\r\n", cal_crc, pack_crc);
        if (cal_crc !=  pack_crc)return false;
      }
    }

  }
  return true;
}

void crc8_init() {
  Serial.println("CRC init");
  for (uint16_t i = 0; i < 256; i++) {
    uint8_t crc = i;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x80) {
        crc = (crc << 1) ^ CRC_POLYNOMIAL;
      } else {
        crc <<= 1;
      }
    }
    crc8_table[i] = crc;
  }
}
