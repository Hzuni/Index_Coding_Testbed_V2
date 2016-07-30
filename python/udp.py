from socket import *
import select

class UdpBroadcaster:
  'Sends broadcast messages to network'
  #addr = ''
  
  def __init__(self, addr=''):
    self.sock = socket(AF_INET, SOCK_DGRAM)
    self.sock.bind((addr, 0))
    self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

  def send(self, message, port=5000):
    self.sock.sendto(message, ('<broadcast>', port))

#import socket, select

class UdpReceiver:
  'Receives UDP packets on the network'

  def __init__(self, port=5000):
    self.sock = socket(AF_INET, SOCK_DGRAM)
    self.sock.bind(('', port))
    self.sock.setblocking(0)

  def rec(self, bufferSize):
    result = select.select([self.sock], [], [])
    return result[0][0].recv(bufferSize)

