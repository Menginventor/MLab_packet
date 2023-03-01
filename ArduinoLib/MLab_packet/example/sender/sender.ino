#include "MLab_packet.h"
MLab_packet dataStreamframe;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  MLab_packet_init();

}
int8_t char_data = 0;
int16_t int_data = 0;
float float_data = 0.0;
void loop() {
  // put your main code here, to run repeatedly:

  dataStreamframe.init();
  dataStreamframe.pack_instruction(0x03);
  dataStreamframe.addDataToPack(char_data);
  dataStreamframe.addDataToPack(int_data);
  dataStreamframe.addDataToPack(float_data);
  dataStreamframe.make_packet();
  //Serial.write(dataStreamframe.tx_buf, dataStreamframe.tx_len());
  delay (100);
  char_data ++;
  int_data ++;
  float_data += 0.1;




}
