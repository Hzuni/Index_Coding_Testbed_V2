__author__ = 'mostlychris modified by Hasun'
from udp import *
from ack_handler import *
import numpy as np
import SVD_enc

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


while True:
    # Get a message
    received_msgs = []

    msg = bytearray(rec.rec(100000))
    msg = msg[0]

    if msg[0] == 'r':
        intended_recipient = msg[1]
        byte_sized_msg = msg[2]
        print(intended_recipient, byte_sized_msg)
        sys.stdout.flush()
        lst_rcv_msg = (intended_recipient, byte_sized_msg)
        r_messages_buffer.append(lst_rcv_msg)

    elif msg[0] == ord('x'):
        x_buffer.append(msg)
        print msg
        # tells AP msg[1] received
        ack_sender.x_ack(me, msg[1])
        # need to reconstruct t here from buffer

    elif msg[0] == ord('m'):
        m = msg[1]
        rows = msg[1]
        columns = msg[2]
        m = np.zeros((rows, columns))
        for i in range(0, rows):
            for j in range(0, columns):
                index = (rows * i + j + 3)
                m[i][j] = msg[index]

    for message in r_messages_buffer:
            received_messages[message[0]][0] = message[1]
            # tells AP message for i_recv has been received
            ack_sender.ack(me, message[0])
            r_messages_buffer.remove(message)

    for i in range(0, num_nodes):
        m_ith_row = m[i][:]
        zeros = np.nonzero(m_ith_row == 0)
        if len(zeros) > 0:
            received_m = 0
        else:
            if i == (num_nodes - 1) :
                received_m = 1
    if received_m == 1:
            # know m need to figure out if X has arrived yet
            req_size = SVD_enc.ready(m)
            # keep x in x_buffer till m received
            if len(x_buffer) == req_size:
                # filling x with x_buffer
                for msg in x_buffer:
                    x_index = msg[1]
                    x[x_index][0] = msg
                    x_buffer = []
                my_msg = SVD_enc.SVDdec(m, x, me, received_msgs)