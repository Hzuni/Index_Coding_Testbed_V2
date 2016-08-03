__author__ = 'Hasun'
from udp import *
from ack_handler import *
import numpy as np
import SVD_enc
import struct
import sys

if len(sys.argv) < 3:
    print("Usage: node.py {id} {num nodes}")
    sys.stdout.flush()
    exit(1)

me = int(sys.argv[1])
num_nodes = int(sys.argv[2])

ack_sender = AckSender("192.168.0.13")
# above meant to send ack to the AP broadcast address

rec = UdpReceiver(5000)


print("Started node at node", me, " with", num_nodes, "total nodes")
sys.stdout.flush()
m = np.zeros((num_nodes, num_nodes))
zero_count = num_nodes * num_nodes

r_messages_buffer = np.zeros((num_nodes, 1))
received_messages = np.zeros((num_nodes, 1))
x_buffer = []
x = np.zeros((num_nodes, 1))
intended_recipient = 0
byte_sized_msg = -256
received_m = 0


while True:
    # Get a message
    received_msgs = []
    msg_received = bytearray(rec.rec(100000))
    msg_received = msg_received[0]

    if msg_received[0] == 'r':
        intended_recipient = msg_received[1]
        byte_sized_msg = msg_received[2]
        print("reieved on initial transmission:", intended_recipient, byte_sized_msg)
        sys.stdout.flush()
        lst_rcv_msg = (intended_recipient, byte_sized_msg)
        r_messages_buffer.append(lst_rcv_msg)

    elif msg_received[0] == ord('x'):
        x_buffer.append(msg_received)
        intended_recipient = msg_received[1]
        byte_sized_msg = msg_received[2]
        print("received following message after initial transmission:", intended_recipient, byte_sized_msg)
        # tells AP msg[1] received
        ack_sender.x_ack(me, msg_received[1])
        # need to reconstruct t here from buffer

    elif msg_received[0] == ord('m'):
        recieved_m = 1 
        rows = msg_received[1]
        columns = msg_received[2]
        m = np.zeros((rows, columns))
        for i in range(0, rows):
            for j in range(0, columns):
                m_ij_bytes = bytearray()
                for k in range(0, 8):
                    byte_k = ( (i * columns * 8) + (j*8) + k+ 3)
                    m_ij_bytes.append(msg_received[byte_k])
                recv_dbl = struct.unpack("d",m_ij_bytes)
                m[i][j] = recv_dbl[0]
        #print(m)



    for message in r_messages_buffer:
            received_messages[message[0]][0] = message[1]
            # tells AP message for i_recv has been received
            ack_sender.ack(me, message[0])
            r_messages_buffer.remove(message)

    if received_m == 1:
            # know m need to figure out if X has arrived yet
            req_size = SVD_enc.ready(m)
            # keep x in x_buffer till m received
            if len(x_buffer) == req_size:
                # filling x with x_buffer
                for msg_received in x_buffer:
                    x_index = msg_received[1]
                    msg_x_bytes = bytearray()
                    for byte_j in range(2, len(msg_received)):
                        msg_x_bytes.append(msg_received[byte_j])

                    x[x_index][0] = struct.unpack("d", bytearray(msg_x_bytes))

                x_buffer = []
                my_msg = SVD_enc.SVDdec(m, x, me, received_msgs)
                print ("My message is ", my_msg)
