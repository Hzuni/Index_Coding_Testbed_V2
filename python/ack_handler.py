import udp
import socket
import threading

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
        self.acks = [[0 for x in range(self.num_nodes)] for x in range(self.num_nodes)]
        for i in range(len(self.acks)):
            self.acks[i][i] = 1
        

    'This is intended to be run as a thread see the start method'
    def listen(self):
        while (self.run):
            ack = None 
            try:
                ack = self.sock.recvfrom(ACK_BUFFER)
                print("Got ack:", ack)
                data = ack[0]
                
                # break of the message into it's info
                node = int (data[0])
                msgId = int (data[1])
                 
                # record the ack
                self.acks[node][msgId] = 2

            # Timeouts will happen, we dont need to do anything
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip

    def ack(self, myId, messageId):
        #print("sending ack for", myId, messageId)
        msg = bytearray([myId, messageId])
        self.sock.sendto(msg, (self.ip, ACK_PORT))

