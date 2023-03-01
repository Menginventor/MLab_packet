import socket
import crc8
import struct
import MLabPacket


def pack_complete (payload):
    pack_idx = MLabPacket.pop_type('B',payload)
    ax = MLabPacket.pop_type('h',payload)
    ay = MLabPacket.pop_type('h', payload)
    az = MLabPacket.pop_type('h', payload)
    gx = MLabPacket.pop_type('h', payload)
    gy = MLabPacket.pop_type('h', payload)
    gz = MLabPacket.pop_type('h', payload)
def client_program():
    host = '192.168.1.57'
    port = 8000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    enable_stream_msg = MLabPacket.makePack(b'\x04', b'\x01')
    client_socket.send(enable_stream_msg)
    packReader = MLabPacket.MlabPack(pack_complete)


    while True:
        rx_data = client_socket.recv(4096)  # receive response
        rx_byte = bytearray(list(rx_data))
        packReader.readData(rx_byte)


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


if __name__ == '__main__':
    client_program()
    # makePack(b'\x04', b'\x00\x00\xff\xff\x00\x00\xff')

