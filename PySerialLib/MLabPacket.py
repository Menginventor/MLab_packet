import crc8
import struct


class MlabPack:
    remain_data = bytearray(0)
    rs_status = 'idle'
    def __init__(self, pack_complete):
        self.pack_complete = pack_complete

    def readData(self,barray):
        self.remain_data.extend(barray)

        if len(self.remain_data) < 4:
            return
        rx_header = bytes([self.remain_data[0], self.remain_data[1]])
        while not rx_header == b'\xff\xff':
            del self.remain_data[0]
            if len(self.remain_data) <2:
                return
            rx_header = bytes([self.remain_data[0], self.remain_data[1]])
            self.rs_status = 'trim header'
        while True:
            if len(self.remain_data) > 4:
                packins = bytes([self.remain_data[2]])
                packlen = self.remain_data[3]
                cobs_overhead = self.remain_data[4]
                # print('ins = ', packins, 'len = ', packlen, 'COBS overhead = ', cobs_overhead)
                total_pack_len = packlen + 5
                # print(total_pack_len,len(remain_data) )
                if len(self.remain_data) > total_pack_len:
                    datapack = self.remain_data[0:total_pack_len]
                    cobs_decoded_pack = cobs_decode(datapack)
                    payload = cobs_decoded_pack[5:total_pack_len - 1]
                    hash = crc8.crc8()
                    hash.update(payload)
                    cal_crc = hash.digest()
                    pack_crc = cobs_decoded_pack[total_pack_len - 1]

                    if cal_crc[0] == pack_crc:
                        self.pack_complete(payload)

                    del self.remain_data[0:total_pack_len]

                else:
                    break

            else:
                break  # wait for the rest of packet


def pop_type (format,payload):
    # print(len(payload))
    data_size = struct.calcsize(format)
    ret = struct.unpack(format, bytes(payload[0:data_size]))

    del payload[0:data_size]

    return ret[0]


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


