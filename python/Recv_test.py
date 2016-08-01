__author__ = 'Hasun'
from udp import *
import numpy as np

rec = UdpReceiver(5000)

while True:
    # Get a message
    received_msgs = []

    msg = bytearray(rec.rec(100000))

    if msg[0] == 'r':
        intended_recipient = msg[1]
        byte_sized_msg = msg[2]
        print(intended_recipient, byte_sized_msg)
        sys.stdout.flush()
        lst_rcv_msg = (intended_recipient, byte_sized_msg)

    elif msg[0] == ord('m'):
        rows = msg[1]
        columns = msg[2]
        print rows
        print columns
        m = np.zeros((rows, columns))
        print(len(msg))
        for i in range(0, rows):
            for j in range(0,columns):
                index = (rows * i + j + 3)
                m[i][j] = msg[index]
        print m

    elif msg[0] == ord('x'):
        print msg[0]
        print msg[1]
        print msg[2]
        # tells AP msg[1] received
        # need to reconstruct t here from buffer

