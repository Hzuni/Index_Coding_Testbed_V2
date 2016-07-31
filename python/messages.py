import random

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
    msg_id = 't'
    msg[0] = msg_id
    return msg

def gen_Matrix_M(m):
    msg = []
    msg_id = 'm'
    msg.append(msg_id)
    msg.append(m)
    return bytearray(msg)