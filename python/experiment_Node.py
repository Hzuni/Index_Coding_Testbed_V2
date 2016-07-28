__author__ = 'mostlychris'
import socket, sys, messages
import decode_manager
from udp import *
from ack_handler import *
import numpy as np
import SVD_enc

if (len(sys.argv) < 3):
    print("Usage: node.py {id} {num nodes}")
    sys.stdout.flush()
    exit(1)

me = int(sys.argv[1])
num_nodes = int(sys.argv[2])

ack_sender = AckSender("10.42.0.1")
#above meant to send acknowldgements to the AP bcast address

rec = UdpReceiver(5000)
decoder = decode_manager.DecodeManager(num_nodes)
#last_tid = -1

print("Started node at node", me, " with", num_nodes, "total nodes")
sys.stdout.flush()
x = np.zeros((len(nodes),i)
m = np.zeros(len(nodes),len(nodes))
zero_count = len(nodes) * len(nodes)
t_buffer = [] 
t = np.zeros((len(nodes),i)

while True:
    # Get a message
    recv_msgs = []
    msg = bytearray(rec.rec(100000))
    
    if (msg[0] == 'r'): 
        intnd_recep = msg[0]
        msg_id = 0 
        byte_sized_msg = msg[1] 
        print(intnd_recep, byte_sized_msg) 
        sys.stdout.flush() 
        lst_rcv_msg = (intnd_recep,msg_id,byte_sized_msg)
        recv_msgs.append(lst_rcv_msg)
        
    elif(msg[0] == 'x'):
        t_buffer.append(msg)
        # need to reconstruct t here from what we get back

    else:
        m = msg[1]        
        

    for message in recv_msgs:
            t[message[0]][0] = message[2]
            ack_sender.ack(me, message[0])
            recv_msgs.remove(message)

    while zero_count != 0:
        zc = 0
        for i in range(0,len(nodes)):
            for j in range(0,len(nodes)):
                if(m[i][j] == 0):
                    zc = zc + 1
                    
        zero_count = zc
        #know m here need to figure out if vector has arrived yet
        req_size = ready(M)
        if (len(t_buffer) == req_size):
            for( msg in t_buffer):
                t_index = msg[1]
                t[t_index] = t_msg

        my_msg = SVD_enc.SVDdec(m,x,me,recv_msgs)


        





                
                

               






               
         
                    

