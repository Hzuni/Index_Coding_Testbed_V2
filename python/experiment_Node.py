__author__ = 'mostlychris modified by Hasun'
import socket, sys, messages
import decode_manager
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

ack_sender = AckSender("10.42.0.1")
# above meant to send ack to the AP broadcast address

rec = UdpReceiver(5000)
decoder = decode_manager.DecodeManager(num_nodes)

print("Started node at node", me, " with", num_nodes, "total nodes")
sys.stdout.flush()


m = np.zeros((num_nodes, num_nodes))
zero_count = num_nodes * num_nodes
t_buffer = [] 
t = np.zeros((num_nodes,1))

while True:
    # Get a message
    recv_msgs = []
    msg = bytearray(rec.rec(100000))
    
    if msg[0] == 'r':
        intnd_recep = msg[0]
        msg_id = 0 
        byte_sized_msg = msg[1] 
        print(intnd_recep, byte_sized_msg) 
        sys.stdout.flush() 
        lst_rcv_msg = (intnd_recep,msg_id,byte_sized_msg)
        recv_msgs.append(lst_rcv_msg)
        
    elif msg[0] == 't':
        t_buffer.append(msg)
        # need to reconstruct t here from buffer

    else:
        m = msg[1]        

    for message in recv_msgs:
            t[message[0]][0] = message[2]
            ack_sender.ack(me, message[0])
            recv_msgs.remove(message)

    while zero_count != 0:
        zc = 0
        for i in range(0,num_nodes):
            for j in range(0,num_nodes):
                if m[i][j] == 0:
                    zc += 1

        zero_count = zc
        if zc != 0:
            break
        else:
            # know m here need to figure out if m has arrived yet
            req_size = SVD_enc.ready(m)

            if len(t_buffer) == req_size:
                # filling t with t_buffer
                for msg in t_buffer:
                    t_index = msg[1]
                    t[t_index] = msg

                t_buffer = []

        my_msg = SVD_enc.SVDdec(m, t, me, recv_msgs)
