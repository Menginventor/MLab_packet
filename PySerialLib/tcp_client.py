import socket
import crc8
import struct
def client_program():
    host = '192.168.1.57'
    port = 8000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    enable_stream_msg = makePack(b'\x04', b'\x01')
    client_socket.send(enable_stream_msg)
    cobs_test_mag = makePack(b'\x04', b'\x00\x00\xff\xff\x00\x00\xff')
    #client_socket.send(cobs_test_mag)

    remain_data = bytearray(0)
    while True:

        rx_data = client_socket.recv(4096)  # receive response

        #print('Received from server: ')  # show in terminal
        #print('rx len', len(rx_data))
        barray = bytearray(list(rx_data))
        remain_data.extend(barray)


        # header trimming
        if len(remain_data) < 4:
            continue
        header = bytes([remain_data[0], remain_data[1]])
        while not header == b'\xff\xff':

            del remain_data[0]
            header = bytes([remain_data[0], remain_data[1]])
            print('trim header')

        while True:
            if len(remain_data) > 4:
                packins = bytes([remain_data[2]])
                packlen = remain_data[3]
                cobs_overhead = remain_data[4]
                #print('ins = ', packins, 'len = ', packlen, 'COBS overhead = ', cobs_overhead)
                total_pack_len = packlen + 5
                #print(total_pack_len,len(remain_data) )
                if len(remain_data) > total_pack_len:
                    datapack = remain_data[0:total_pack_len]

                    cobs_decoded_pack = cobs_decode(datapack)

                    payload = cobs_decoded_pack[5:total_pack_len-1]
                    hash = crc8.crc8()
                    hash.update(payload)
                    cal_crc = hash.digest()
                    pack_crc = cobs_decoded_pack[total_pack_len-1]
                    print(payload)
                    # print('CRC',cal_crc[0],pack_crc)
                    if len(payload) == 56 and cal_crc[0] == pack_crc:
                        unpack = struct.unpack('H27h',bytes(payload))

                        unpack_str  = [str(code) for code in unpack]
                        print('\t'.join(unpack_str))
                    del remain_data[0:total_pack_len]

                else:
                    break

            else :
                break # wait for the rest of packet

        #print(remain_data[0:60])
        #remain_data = bytearray(0)

    client_socket.close()  # close the connection


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
    client_program()
    # makePack(b'\x04', b'\x00\x00\xff\xff\x00\x00\xff')

