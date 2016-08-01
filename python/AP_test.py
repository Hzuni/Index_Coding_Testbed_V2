import numpy as np
import udp
import messages
MY_IP = '192.168.0.13'

# Setup the udp broadcaster
broadcaster = udp.UdpBroadcaster(MY_IP)
A = np.zeros((9, 9))
for i in range(0, len(A)):
    A[i][i] = 8

#msg =  messages.gen_Matrix_M(A)
msg2 = messages.gen_message(1)
msg3 = messages.set_messageId_x(msg2)
#broadcaster.send(msg, 5000)
broadcaster.send(msg3,5000)
