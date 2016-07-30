import random

def gen_message(i_recv):
# Repersents initial message by marking it with r
    msg = []
    rand = random.Random()
    rand.seed(i_recv)
    msg.append('r')
# Building the message
    msg.append(i_recv)
# Intended recipient of node message
    byte = rand.getrandbits(8)
    msg.append(byte)
    return bytearray(msg)
    
def set_messageId_t(message):
    message[0] = 't'
    return message

def gen_Matrix_M(m):
    msg = []
    msg_id = 'm'
    msg.append(msg_id)
    msg.append(m)
    return bytearray(msg)