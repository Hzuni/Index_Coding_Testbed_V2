#client example
import socket
import os
import time

port = 9999 # Make this whatever port you want to use. It should match your server.py port.
address = 'localhost' # Change this to whatever address the server is

command = raw_input('Enter a command: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
client_socket.connect((address, port))
client_socket.send(command)
time.sleep(3)

msg=client_socket.recv(1024)
client_socket.close()
    
print msg
