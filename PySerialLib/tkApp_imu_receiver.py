import socket
import MLabPacket
import threading
import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import time
# Create a Tkinter window



# Define the update function
def update(frame):
    # Clear the plot
    data_display = 250*5
    if len(ax_list) == 0:
        return
    ax1.clear()
    ax2.clear()
    # Add the new data point
    data_ax = ax_list
    if len(data_ax) > data_display:
        data_ax = data_ax[len(data_ax) - data_display:len(data_ax)]
    data_ay = ay_list
    if len(data_ay) > data_display:
        data_ay = data_ay[len(data_ay) - data_display:len(data_ay)]
    data_az = az_list
    if len(data_az) > data_display:
        data_az = data_az[len(data_az) - data_display:len(data_az)]

    data_gx = gx_list
    if len(data_gx) > data_display:
        data_gx = data_gx[len(data_gx)-data_display:len(data_gx)]
    data_gy = gy_list
    if len(data_gy) > data_display:
        data_gy = data_gy[len(data_gy) - data_display:len(data_gy)]
    data_gz = gz_list
    if len(data_gz) > data_display:
        data_gz = data_gz[len(data_gz) - data_display:len(data_gz)]
    # Plot the data
    ax1.plot(data_ax)
    ax1.plot(data_ay)
    ax1.plot(data_az)

    ax2.plot(data_gx)
    ax2.plot(data_gy)
    ax2.plot(data_gz)

    # Set the axis labels
    #ax1.set_xlabel("Time")
    ax1.set_ylabel("acc")
    ax2.set_ylabel("gyro")

    # Adjust the plot limits
    #ax.set_xlim(0, len(data_xx))
    #ax.set_ylim(min(data_ax), max(data_ax))

    # Redraw the plot
    canvas.draw()





ax_list = []
ay_list = []
az_list = []
gx_list = []
gy_list = []
gz_list = []

def pack_complete (payload):
    pack_idx = MLabPacket.pop_type('H',payload)
    accx = MLabPacket.pop_type('h',payload)
    accy = MLabPacket.pop_type('h', payload)
    accz = MLabPacket.pop_type('h', payload)
    gx = MLabPacket.pop_type('h', payload)
    gy = MLabPacket.pop_type('h', payload)
    gz = MLabPacket.pop_type('h', payload)

    ax_list.append(accx)
    ay_list.append(accy)
    az_list.append(accz)
    gx_list.append(gx)
    gy_list.append(gy)
    gz_list.append(gz)

    #print(pack_idx,accx,accy,accz,gx,gy,gz)

def client_program():
    #host = '192.168.1.57'
    host = '192.168.4.1'
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


def connect_btn_cb():
    global connect_flag
    connect_flag = True
    print('connect_btn_cb')
    client_thread = threading.Thread(target=client_program)

    # Start the thread
    client_thread.start()

def disconnect_btn_cb():
    global connect_flag
    connect_flag = True
    print('disconnect_btn_cb')

def record_btn_cb():

    print('record_btn_cb')
    global ax_list
    global ay_list
    global az_list
    global gx_list
    global gy_list
    global gz_list

    ax_list = []
    ay_list = []
    az_list = []
    gx_list = []
    gy_list = []
    gz_list = []


def stop_btn_cb():

    print('stop_btn_cb')
    data_matrix = np.array([ax_list,ay_list,az_list,gx_list,gy_list,gz_list])
    print(data_matrix.shape)

    timestr = time.strftime("%Y%m%d-%H%M%S")
    np.save(timestr, data_matrix)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Real-Time Plot")

    # Create a Matplotlib figure
    fig = plt.Figure()

    # Add a subplot to the figure
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    # Create a list to store the data
    data = []
    st = ttk.Style()
    st.configure('W.TButton', background='#345', foreground='black', font=('Arial', 14))
    frame = tk.Frame( root,relief=tk.RAISED, borderwidth=1)
    frame.pack()

    connect_btn = ttk.Button(frame, text="connect", command=connect_btn_cb)
    disconnect_btn= ttk.Button(frame, text="disconnect", command=disconnect_btn_cb)

    rec_btn = ttk.Button(frame, text="Record", command=record_btn_cb)
    stop_btn = ttk.Button(frame, text="Stop", command=stop_btn_cb)
    # Set the position of button on the top of window.
    connect_btn.pack(side='left')
    disconnect_btn.pack(side='left')
    rec_btn.pack(side='left')
    stop_btn.pack(side='left')


    # Create a Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create an animation
    ani = FuncAnimation(fig, update, interval=50)

    # Start the Tkinter event loop
    # Create a Button


    root.mainloop()




