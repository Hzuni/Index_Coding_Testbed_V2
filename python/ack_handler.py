import socket
import threading
import numpy as np

ACK_PORT = 5005
ACK_TIMEOUT = 1
ACK_BUFFER = 256

class AckListener:
    'Handles ack messages and tracking'

    def __init__(self, numNodes):
        # set up acks list
        self.num_nodes = numNodes
        self.reset()
       
        # UDP socket setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("10.42.0.1", ACK_PORT))
        self.sock.settimeout(ACK_TIMEOUT)
        self.timeouts = 0
        
        # Set running flag
        self.run = False

    def reset(self):
        #self.acks = [[0 for x in range(self.num_nodes)] for x in range(self.num_nodes)]
        self.acks = np.zeros((self.num_nodes,self.num_nodes))
        self.U = np.zeros(( self.num_nodes,self.num_nodes))
        # empty array, will fill with 1s until everyone has M
        self.G = np.zeros((self.num_nodes,1))

        # for i in range(len(self.acks)):
        #    self.acks[i][i] = 1
    def set_U(self,x_len):
        # set U to be an x by numNodes Matrix
        self.U = np.zeros((x_len, self.num_nodes))
        

    # This is intended to be run as a thread see the start method
    def listen(self):
        while (self.run):
            ack = None 
            try:
                ack = self.sock.recvfrom(ACK_BUFFER)
                data = ack[0]
                
                # break of the message into it's info
                ack_mode = int(data[0])
                node = int(data[1])

                if ack_mode == 'r':
                    # tells us that the ack was a message
                    msg_id = int(data[2])

                    # TODO: Is this the correct format?
                    if (node == msg_id):
                        self.acks[node][msg_id] = 1
                    else:
                        self.acks[node][msg_id] = 2

                elif ack_mode == 'm':
                    # Node received matrix m
                    self.G[node][0] = 1

                elif ack_mode == 'x':
                    # tells us that node ack was for a received message of x
                    msg_id = int(data[2])
                    self.U[msg_id][node] = 1


            # Timeouts will happen, we don't need to do anything
            except socket.timeout:
                self.timeouts += 1

    def start(self):
        self.run = True
        self.stopped = False
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def stop(self):
        self.run = False
        self.thread.join()

class AckSender:
    'Handles the sending of acks so we can have a standard format'

    def __init__(self, ip):
        # type: (object) -> object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip

    def ack(self, myid, message_id):
        ack_mode = 'r'
        msg = bytearray([ack_mode, myid, message_id])
        self.sock.sendto(msg, (self.ip, ACK_PORT))

    def matrix_ack(self, myid):
        # An acknowledgement telling the AP the matrix has been received
        ack_mode = 'm'
        msg = bytearray([ack_mode, myid])
        self.sock.sendto(msg, (self.ip, ACK_PORT))

    def x_ack(self,myid, message_id):
        # An acknowledgement telling AP a message from X has been received
        ack_mode = 'x'
        msg = bytearray([ack_mode, myid, message_id])
        self.sock.sendto(msg, (self.ip, ACK_PORT))

