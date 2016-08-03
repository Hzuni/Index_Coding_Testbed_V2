import random
import numpy as np
import struct

def gen_message(i_recv):
    # Represents initial transmission with r
    msg = []
    rand = random.Random()
    rand.seed(i_recv)
    msg_id = 'r'
    msg.append(msg_id)
    # Building the message
    msg.append(i_recv)
    # Intended recipient of node message
    byte = rand.getrandbits(8)
    msg.append(byte)
    return bytearray(msg)
    
def gen_X_message(index, x_msg):
    msg = []
    msg_id = 'x'
    msg.append(msg_id)
    msg.append(index)
    msg = bytearray(msg)
    x_msg_ba = bytearray(struct.pack("d",x_msg))
    for i in range (0,len(x_msg_ba)):
        msg.append(x_msg_ba[i])

    print(msg)
    return msg

def gen_Matrix_M(m):
    msg = []
    msg_id = 'm'
    rows = len(m)
    columns = len(m[0])
    msg.append(msg_id)
    msg.append(rows)
    msg.append(columns)
    msg = bytearray(msg)
    for i in range(0,rows):
        for j in range(0, columns):
            j_msg = m[i][j]
            j_msg_ba = bytearray(struct.pack("d", j_msg))
            for k in range(0, len(j_msg_ba)):
                msg.append(j_msg_ba[i])
    return msg