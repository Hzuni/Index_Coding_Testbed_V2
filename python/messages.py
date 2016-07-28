import random
import algorithms
import encoding, decoding
from math import log

#TEST_INDEX = 0
#COUNT_INDEX = 1
#COEFFS_SIZE_INDEX = 2
#COEFFS_INDEX = 3

#def gen_messages(num, length):
#    'This method generates random data to act as a message'

#    msgs = []
#    for i in range(0, num):
#        data = gen_data(i, length)
#        msgs.append(data)

#    return msgs

def gen_message(i_recv):
   # The message should be repersented as a byte array with an indented
   # reciepent appended to the begining.

    msg = [] 
    rand = random.Random()
    rand.seed(i_recv))
    msg_Id = 'r'
    msg.append(msg_Id)

    #Building the message 
    msg.append(i_recv)   
   #Intended reciepient of node message
    
    byte = rand.getrandbits(8)
    msg.append(byte)
    return bytearray(msg)
    
def set_messageId_x(message):
    message[0] = 'x'
    return message

def gen_Matrix_M(m):
    msg = []
    msg_Id = 'm'
    msg.append(msg_Id)
    msg.append(m)
    return bytearray(msg)












#def gen_data(seed, length):
#    'Generates random data in bytes of the specified length'

#    rand = random.Random()
#    rand.seed(seed)

#    data = []
#    for i in range(0, length):
#        byte = rand.getrandbits(8)
#        data.append(byte)

#    return bytearray(data)


#def get_test(msg):
#    return msg[TEST_INDEX]


#def get_data(msg):
#    num = msg[COUNT_INDEX]
#    coeff_size = msg[COEFFS_SIZE_INDEX]
#    return msg[COEFFS_INDEX + num + (num * coeff_size):]


#def get_coeffs(msg, num_nodes):
#    num = msg[COUNT_INDEX]
#    coeff_size = msg[COEFFS_SIZE_INDEX]
#    coeffs = [0] * num_nodes
    
#    for i in range(num):
#        id_index = COEFFS_INDEX + i + (i * coeff_size)
#        coeff_index = id_index + 1
#        coeff_index_end = coeff_index + coeff_size

#        msg_id = msg[id_index]
#        if coeff_size > 0:
#            coeff = int.from_bytes(msg[coeff_index : coeff_index_end], byteorder='big', signed=True)
#        else:
#            coeff = 1

#        coeffs[msg_id] = coeff
        
#    return coeffs


#'This is passed a row from the processed matrix to generate that message'
#def encode_row(row, msgs, tid, coeff_size):
#    header = [tid, 0, coeff_size]
#    msg = encoding.EncodedMessage(0, rawEncoding=True)
#    mod_factor = ((2**(coeff_size * 8)) // 2) - 1;

#    for i in range(len(row)):    
        # for now, nothings are ignored
#        if row[i] != 0 and row[i] != algorithms.DONT_CARE:
#            header[COUNT_INDEX] += 1
#            header.append(i)
            
#            if abs(row[i]) >= mod_factor and coeff_size > 0:
#                negative = row[i] < 0
                #print("WARNING: We went outside of our encoding range. coeff:", row[i])
#                row[i] = row[i] % mod_factor
#                if negative:
#                    row[i] *= -1
#            
#            if coeff_size > 0: 
#                header.extend(row[i].to_bytes(coeff_size, byteorder='big', signed=True))
#            else:
#                assert row[i] == 1
#            
#            msg = msg + (encoding.EncodedMessage(msgs[i]) * row[i])
    
#    if header[COUNT_INDEX] > 0:
#        header = bytearray(header)
#        return header + msg.toBytes(removeMarker=False)
#    else:
#        return None       

