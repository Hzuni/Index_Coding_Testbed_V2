import select, socket 
from udp import *

port = 50000  # where do you expect to get a msg?
bufferSize = 1024 # whatever you need

rec = UdpReceiver(port)
while True:
  print rec.rec(bufferSize)
'''s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)

while True:
  result = select.select([s],[],[])
  msg = result[0][0].recv(bufferSize) 
  print msg
'''
