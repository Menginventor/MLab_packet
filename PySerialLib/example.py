import socket
import crc8
import struct
import serial
import serial.tools.list_ports

buadrate = 115200

def main():
    while True:
        portlist = serial.tools.list_ports.comports()
        print('Select serial port')
        for port_idx in range(len(portlist)):
            port = portlist[port_idx]
            print('[%d] %s' % (port_idx,port.name))
        userSelectedPortIdxStr = input()
        if int(userSelectedPortIdxStr) >= 0 and int(userSelectedPortIdxStr) < len(portlist):
            userSelectedPortIdx = int(userSelectedPortIdxStr)
            UserSelectedPort = portlist[userSelectedPortIdx]
            print('Connect to %s' % UserSelectedPort.name)
            try:
                ser = serial.Serial(UserSelectedPort.name, buadrate)
            except serial.SerialException:
                print(f"Error: {UserSelectedPort} is already open or unavailable.")
                continue
            break


    remain_data = bytearray(0)
    while True:
        if ser.inWaiting() > 0:
            rx_data = ser.read()

            barray = bytearray(list(rx_data))
            remain_data.extend(barray)

            if len(remain_data) < 4:
                continue
            rx_header = bytes([remain_data[0], remain_data[1]])
            while not rx_header == b'\xff\xff':
                del remain_data[0]
                rx_header = bytes([remain_data[0], remain_data[1]])
                print('trim header')
            while True:
                if len(remain_data) > 4:
                    packins = bytes([remain_data[2]])
                    packlen = remain_data[3]
                    cobs_overhead = remain_data[4]
                    # print('ins = ', packins, 'len = ', packlen, 'COBS overhead = ', cobs_overhead)
                    total_pack_len = packlen + 5
                    # print(total_pack_len,len(remain_data) )
                    if len(remain_data) > total_pack_len:
                        datapack = remain_data[0:total_pack_len]
                        cobs_decoded_pack = cobs_decode(datapack)
                        payload = cobs_decoded_pack[5:total_pack_len - 1]
                        hash = crc8.crc8()
                        hash.update(payload)
                        cal_crc = hash.digest()
                        pack_crc = cobs_decoded_pack[total_pack_len - 1]

                        if cal_crc[0] == pack_crc:



                            signed_char = struct.unpack('b', bytes(payload[0:1]))
                            signed_int = struct.unpack('h', bytes(payload[1:3]))
                            signed_float = struct.unpack('f', bytes(payload[3:7]))
                            #print(payload)
                            print(signed_char)
                            print(signed_int)
                            print(signed_float)

                        del remain_data[0:total_pack_len]

                    else:
                        break

                else:
                    break  # wait for the rest of packet

            # print(remain_data[0:60])
            # remain_data = bytearray(0)






def cobs_decode(encoded_pack): # recieve byte_array
    #print(list(encoded_pack))
    cobs_overhead = encoded_pack[4]
    code_idx = int(cobs_overhead)+4
    decoded_pack = encoded_pack[:]

    while code_idx < len(encoded_pack):

        decoded_pack[code_idx] = 255
        code_idx += int(encoded_pack[code_idx])
        if code_idx == 0:
            print('Error cobs')
            return None

    return decoded_pack




def makePack(ins, payload):
    packet = bytearray(b'\xff\xff')
    packet.extend(ins)

    packlen = bytes([len(payload)+1])
    packet.extend(packlen)


    hash = crc8.crc8()
    hash.update(payload)
    crc = hash.digest()
    payload_crc = bytearray(payload)
    payload_crc.extend(crc)
    print('crc = ',crc)
    print('payload_crc', payload_crc)
    cobs_packet = cobs(payload_crc)
    print('cobs_packet', cobs_packet)
    packet.extend(cobs_packet)
    print(packet)
    return packet

def cobs(payload):
    cobs_packet = bytearray(b'\x01')
    cobs_packet.extend(payload)
    code_idx = 0
    code_val = 1
    delimiter = bytes(b'\xff')

    for idx in range(1,len(cobs_packet)):
        crr_byte = bytes([cobs_packet[idx]])

        if crr_byte == delimiter:
            cobs_packet[code_idx] = code_val
            code_val = 1
            code_idx = idx
        else:
            code_val += 1
    else:
        cobs_packet[code_idx] = code_val
    return cobs_packet


if __name__ == '__main__':
    main()
    # makePack(b'\x04', b'\x00\x00\xff\xff\x00\x00\xff')

