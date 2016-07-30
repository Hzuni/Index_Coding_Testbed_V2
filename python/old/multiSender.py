# UDP multicast examples, Hugo Vincent, 2005-05-14.
import socket

def send(data, port=50000, addr='10.42.0.1'):
	"""send(data[, port[, addr]]) - multicasts a UDP datagram."""
	# Create the socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# Make the socket multicast-aware, and set TTL.
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20) # Change TTL (=20) to suit
	# Send the data
	s.sendto(data, (addr, port))

if __name__ == "__main__":
	send("hi from me")
