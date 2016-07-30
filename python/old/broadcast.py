# Send UDP broadcast packets

MYPORT = 50000

from udp import *

broad = UdpBroadcaster('10.42.0.1')
broad.send("hello", 50000)

'''import sys, time
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('10.42.0.1', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while 1:
  data = repr(time.time()) + '\n'
  s.sendto(data, ('<broadcast>', MYPORT))
  print "broadcast sent"
  time.sleep(2)'''
