 void handleTcpData(void *arg, AsyncClient *client, void *data, size_t len)
{
  Serial.printf("\n data received from client %s \n", client->remoteIP().toString().c_str());
  //Serial.write((uint8_t *)data, len);
  for (int i = 0; i < len; i++) {
    Serial.printf("0x%02x,", ((uint8_t *)data)[i]);
  }
  Serial.println();

  MLab_packet dataframe;
  dataframe.load_buf((uint8_t *)data, len);
  Serial.print("Verify header ");
  Serial.println(dataframe.verify_header());

  uint8_t packins = dataframe.get_ins();

  Serial.print("dataframe\'s ins");
  Serial.println(packins);

  Serial.print("dataframe\'s packlen");
  uint8_t packlen = dataframe.get_packlen();
  Serial.println(packlen);
  uint8_t buf[254];
  bool crc_check = dataframe.decodeCOBS(buf);
  Serial.println("decoded COBS");
  for (int i = 0; i < packlen; i++) {
    Serial.printf("0x%02x,", buf[i]);
  }
  Serial.println();
  //
  Serial.printf("CRC check:%s", crc_check ? "true" : "false");

  if (packins == 0x04) {
    bool data_val = buf[0];
    if (data_val == 0x00) {
      Serial.println("Disable data streaming");
      data_stream_flag = false;
    }
    else if (data_val == 0x01) {
      Serial.println("Enable data streaming");
      data_stream_flag = true;
    }
    else {
      Serial.printf("Error, unknow value (0x%02x)", data_val);
    }
  }


}

 void handleTcpError(void *arg, AsyncClient *client, int8_t error)
{
  Serial.printf("\n connection error %s from client %s \n", client->errorToString(error), client->remoteIP().toString().c_str());
}

 void handleTcpDisconnect(void *arg, AsyncClient *client)
{
  Serial.printf("\n client %s disconnected \n", client->remoteIP().toString().c_str());
  data_stream_flag = false;
}

 void handleTcpTimeOut(void *arg, AsyncClient *client, uint32_t time)
{
  Serial.printf("\n client ACK timeout ip: %s \n", client->remoteIP().toString().c_str());
}

 void handleTcpNewClient(void *arg, AsyncClient *client)
{
  Serial.printf("\n new client has been connected to server, ip: %s\r\n", client->remoteIP().toString().c_str());
  // register events
  client->onData(&handleTcpData, NULL);
  client->onError(&handleTcpError, NULL);
  client->onDisconnect(&handleTcpDisconnect, NULL);
  client->onTimeout(&handleTcpTimeOut, NULL);
  dataStreamClient = client;
  data_stream_flag = false;
  stream_pack_idx = 0;
}
