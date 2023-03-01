#ifndef _MLabPACKET_H_
#define _MLabPACKET_H_

#include <cstring>
#include <Arduino.h>

#define COBS_DELIMITER 0xFF  // Delimiter byte for COBS
#define COBS_MAX_PAYLOAD_LENGTH 254  // Maximum length of the payload in a COBS packet

#define CRC_POLYNOMIAL 0x07  // Polynomial used for CRC calculation


extern  uint8_t crc8_table[256];

class MLab_packet {
  private:
    uint8_t pack_idx = 0;
    uint8_t payload_len = 0;
    const uint8_t head_offset = 5;// 2 header, 1 instruction, 1 pack-len, 1-COB

    uint8_t pack_crc;


  public:
    uint8_t tx_len();
    uint8_t tx_buf[256];


    void init() ;
    void pack_header() ;
    void pack_instruction(uint8_t ins);
    void pack_len() ;

    ///
    template<typename T>
    void addDataToPack(T var) {
      memcpy(tx_buf + head_offset + payload_len, reinterpret_cast<const byte*>(&var), sizeof(var));
      payload_len += sizeof(var);
    }
    void printPayload() ;
    void printPacket();
    void make_packet();

    void crc8();

    void encodeCOBS();
    void load_buf(uint8_t *src, size_t len);
    bool verify_header();
    uint8_t get_ins();
    uint8_t get_packlen();
    bool decodeCOBS(uint8_t *dst);

};

void crc8_init();
void MLab_packet_init();
#endif
