__author__ = 'mostlychris'
import socket, sys, messages
import decode_manager
from udp import *
from ack_handler import *

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

while True:
    # Get a message
    recv_msgs = []
    msg = bytearray(rec.rec(100000))
    #tid = messages.get_test(msg)
    #coeffs = messages.get_coeffs(msg, num_nodes)
    #data = messages.get_data(msg)
    intnd_recep = msg[0]
    msg_id = 0 
    byte_sized_msg = msg[1] 
    print(intnd_recep, byte_sized_msg) 
    sys.stdout.flush() 
   
    lst_rcv_msg = (intnd_recep,msg_id)
    recv_msgs.append(lst_rcv_msg)


    #intended to transmit a message with the message id 
#    ack_sender.ack(me,message_id)

#    if (tid == (last_tid + 1) or (tid != last_tid and tid == 0 and last_tid > 50)):
#        print("New test... Reseting.\nTID:", tid)
#        sys.stdout.flush()
#        decoder.reset()
#        last_tid = tid

#    new_decoded = []
#    if not decoder.can_decode(me):
#        new_decoded = decoder.addMessage(coeffs, data)

#    if me in new_decoded:
#        decoded = decoder.decode_message(me)
#        size = len(decoded)
#        should_be = messages.gen_data(me, size)
#        if decoded == should_be:
#            print ("Correctly decoded message")
#        else:
#            print ("ERROR: incorrect decoding \nExpected len:", len(should_be), "\nFound:", len(decoded))
#            print ("Expected message:", should_be, "\nfound:",decoded)
#        sys.stdout.flush()

    # make sure the AP knows we can decode
#    if coeffs[me] != 0 and decoder.can_decode(me):
#        new_decoded.append(me)

    for message in recv_msgs:
        ack_sender.ack(me, message[0])
        recv_msgs.remove(message)


