import random
import numpy as np

def gen_message(i_recv):
# Repersents initial transmission with r
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
    
def set_messageId_x(msg):
    msg_id = 'x'
    msg[0] = msg_id
    return msg

def gen_Matrix_M(m):
    msg = []
    msg_id = 'm'
    rows = len(m)
    columns = len(m[0])
    msg.append(msg_id)
    msg.append(rows)
    msg.append(columns)
    for i in range(0,rows):
        for j in range(0, columns):
            msg.append(ord(bytes(m[i][j])[0]) - ord('0'))
            print(m[i][j])
    return bytearray(msg)