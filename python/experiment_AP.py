import udp
import socket
import ack_handler
import algorithms
import signal 
import sys
import messages
from time import sleep,time
#import matplotlib.pyplot as plt
#import pickle
#import statistics
#from copy import deepcopy

# Static Variables
nodes = sys.argv[1].split()
log_dir = sys.argv[2]
nodes = list(map(int, nodes))
nodes.sort()

# Networking
PORT = 5000
MY_IP = '10.42.0.1'
# Dataset
MSG_LEN = 500
NUM_TESTS = 10
# Data cleaning 
CLEAN_DATA = False # this should probably stay off
CLEAN_FACTOR = 3
# Timeouts
ROUNDS_TIMEOUT = 100
# Aglorithms used 
# "rr" = Round Robin
# "ldg" = least difference geedy
# "svdap" = SVD alternating projection
#ENCODE_ALGOS = ["rr", "ldg", "svdap"]
# Sleep times
SLEEP_BROADCASTS = 0.002
SLEEP_TESTS = 1.0
# save acks for debugging
SAVE_ACKS = True

# Code for expriments starts here
print("Starting experiment with nodes: ", nodes) # "using", ENCODE_ALGOS)

# setup the ack listener
#acks = ack_handler.AckListener(len(nodes))
acks = ack_handler.AckListener(8)


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
msgs = []
#msgs = messages.gen_messages(len(nodes), MSG_LEN)

# set up stats
#num_algos = len(ENCODE_ALGOS)
tests = []
rounds = []
test_time = []
lost_msgs = []
lost_by_owner_msgs = []
encode_time = []
msgs_sent = []
msgs_saved = []
msg_correlations = []
loss_avg = []
saved_acks = []
#for algo_index in range(num_algos):
#    tests.append([])
#    rounds.append([])
#    test_time.append([])
#    lost_msgs.append([])
#    lost_by_owner_msgs.append([])
#    encode_time.append([])
#    msgs_sent.append([])
#    msgs_saved.append([])
#    msg_correlations.append([])
#    loss_avg.append([])

#for test in range(NUM_TESTS):
#    for algo_index in range(num_algos):
#algo = ENCODE_ALGOS[algo_index]
#print("Starting experiment", test, algo)
sys.stdout.flush()
rnd = 0
lost = 0
lost_by_owner = 0
encodings = 0
encode_time = 0
sent = 0
test_start = time()
rank_diff = 0
msg_correlation = 0
loss = 0
saved_acks.append([])
messages_to_create = 8
   

# first round is always round robin
#tid = ((test * num_algos) + algo_index) % 128
#toSend = algorithms.reduceMessages(msgs, acks.acks, tid, algo="rr")
#failed = False

#while (len(toSend) > 0 and not failed):
#    rnd += 1

#if (rnd > 20):
#    print("spiking with nodes", messages.get_nodes(toSend[0]))
for i in range(0,messages_to_create):
    message_i = messages.gen_message(i)
    msgs.append(message_i)


for message in msgs:
    broadcaster.send(message, PORT)
    sleep(SLEEP_BROADCASTS)
    sent += 1
    sleep(0.05)

for i in range(8):
    if (acks.acks[i][i] == 1):
        lost_by_owner += 1

print (lost_by_owner)       
print("\nShutting down...\n")
sys.stdout.flush()
acks.stop()
sys.exit(0)
