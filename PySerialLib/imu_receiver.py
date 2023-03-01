import socket
import MLabPacket
import threading


ax_array = []
ay_array = []
az_array = []
gx_array = []
gy_array = []
gz_array = []

def pack_complete (payload):
    pack_idx = MLabPacket.pop_type('H',payload)
    ax = MLabPacket.pop_type('h',payload)
    ay = MLabPacket.pop_type('h', payload)
    az = MLabPacket.pop_type('h', payload)
    gx = MLabPacket.pop_type('h', payload)
    gy = MLabPacket.pop_type('h', payload)
    gz = MLabPacket.pop_type('h', payload)

    ax_array.append(ax)
    ay_array.append(ay)
    az_array.append(az)
    gx_array.append(gx)
    gy_array.append(gy)
    gz_array.append(gz)

    print(pack_idx,ax,ay,az,gx,gy,gz)

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



if __name__ == '__main__':
    client_thread = threading.Thread(target=client_program)

    # Start the thread
    client_thread.start()



