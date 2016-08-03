#!/usr/bin/env python

import SocketServer
from time import sleep
import os
import base64

#################### Program Starts #####################

class YourCustomClass():

    # def __init__(self, error):

        # Members

    def your_routine_1(self):
        return "We just did routine 1!"

    def your_routine_2(self):
        return "We just did routine 2!"

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
    
        # Split the command based on whitespace
        client_inputs = str.split(self.data)
        response = None

        if(client_inputs[0] == "routine1"):
            response = self.server.custom_class.your_routine_1()
        elif(client_inputs[0] == "routine2"):
            response = self.server.custom_class.your_routine_2()
        else:
            response = "BUG: Bad routine call from client."

        if response:
            self.request.sendall(response)

class MyServer(SocketServer.ThreadingTCPServer):

    def __init__(self, server_address, RequestHandlerClass, node):
        SocketServer.allow_reuse_address = True
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.custom_class = custom_class


####################### Main #######################

if __name__ == "__main__":
    HOST, PORT = "", 9999

    # Sets up GPIO for a primary node
    custom_class = YourCustomClass()

    # Create the server, binding to localhost on port 9999
    # server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server = MyServer((HOST, PORT), MyTCPHandler, custom_class)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

