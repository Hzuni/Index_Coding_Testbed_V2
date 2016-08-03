import numpy as np
import udp
import messages
import message_test
#MY_IP = '192.168.0.13'

m = np.zeros((5,5))
m[0][1] = 5.05
m[0][0] = 7.92347
m[1][4] = 6.9895
m[3][2] = 6.4333312
m[4][4] = 2.98555
print (m)

message_m = messages.gen_Matrix_M(m)
print(message_m)

message_test.matrix_receiver(message_m)


