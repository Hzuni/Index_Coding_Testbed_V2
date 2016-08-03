import udp
import ack_handler
import signal
import sys
import messages
from time import sleep
import SVD
import SVD_enc
import numpy as np

# Static Variables
nodes = sys.argv[1].split()
log_dir = sys.argv[2]
nodes = list(map(int, nodes))
nodes.sort()

# Networking
PORT = 5000
MY_IP = '10.42.0.1'

# Timeouts
ROUNDS_TIMEOUT = 100

# Sleep times
SLEEP_BROADCASTS = 0.002
SLEEP_TESTS = 1.0
# save acks for debugging
SAVE_ACKS = True

# Code for expriments starts here
print("Starting experiment with nodes: ", nodes) # "using", ENCODE_ALGOS)

# setup the ack listener
acks = ack_handler.AckListener(len(nodes))


# setup shutdown listener
def signal_handler(signal, frame):
    print("\nShutting down...\n")
    acks.stop()
    sys.stdout.flush()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# start ack listener
acks.start()

# Setup the udp broadcaster
broadcaster = udp.UdpBroadcaster(MY_IP)

# generate messages, 1 per nodes right now
sent = 0

print("Running the experiment using SVD and RoundRobin")
sys.stdout.flush()

N = len(nodes)
messages_to_create = len(nodes)

# T holds all of the originally created messages
T = np.zeros((N,1))
T_msgs = []

# Placing the messages inside vector T
for i in range(0,messages_to_create):
    message_i = messages.gen_message(i)
    T_msgs.append(message_i)
    T[i][0] = int(message_i[2])

for i in range(0, messages_to_create):
    #Prints the random byte each node should be receiving
    print("Node ", i, "should recieve ", T[i][i] )

for message in T_msgs:
    broadcaster.send(message, PORT)
    sleep(SLEEP_BROADCASTS)
    sent += 1
    sleep(0.05)

M = acks.acks

# send X and M until all receivers have them
#red_matrix = SVD.reduce(acks.acks)
[Rmin,OptM] = SVD.APIndexCode(acks.acks)

X = SVD_enc.SVDenc(OptM,T, Rmin)

# send X and M until all receivers have them
end = 1

# X by N empty matrix, will fill with 0s until everyone has all of X
acks.set_U(len(X))

U = acks.U

# Init
count = 0
round = 0


while end:
        # Send all messages of X
        for i in range(len(X)):
            tem = U[i][:]
            left = np.nonzero(tem == 0)
            # If everyone has X messages, don't resend it
            if len(left[0]) > 0:
                xmessage_i = messages.gen_X_message(i,X[i])
                broadcaster.send(X[i], PORT)

        # Send M to everyone
        num_left = np.nonzero(acks.G == 0)
        # If everyone has OptM, don't resend it
        if len(num_left[0]) > 0:
            count += 1
            optm_message = messages.gen_Matrix_M(OptM)
            broadcaster.send(optm_message, PORT)
            num_left = np.nonzero(acks.G == 0)

        # increment round
        round += 1
        zeros = np.nonzero(U == 0)
        # If everyone has all the messages and the matrix, exit while loop of sending
        if len(zeros[0]) == 0 and len(num_left[0]) == 0:
            end = 0
print("Count value for SVD is:", count)

exit = 1

while (exit):
   for i in range(N):
       # IF the receiver that wants the message, has it, don't resend
       if M[i][i] == 0:
           count += 1
           broadcaster.send(T[i])

   round += 1
   diag = np.nonzero(M == 1)
   if len(diag[0]) == N:
       exit = 0
print("Count value for RR is:", count)


print("\nShutting down...\n")
sys.stdout.flush()
acks.stop()
sys.exit(0)
