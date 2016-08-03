import random
import time
from math import log, ceil

class EncodedMessage:
	def __init__(self, message, rawEncoding=False, addMarker=True):
		if rawEncoding:
			self.encoding = message
		else:
			self.encoding = self.fromBytes(message, addMarker)
	
	def __add__(self, other):
		return EncodedMessage(self.encoding + other.encoding, rawEncoding=True)

	def __sub__(self, other):
		return EncodedMessage(self.encoding - other.encoding, rawEncoding=True)

	def __mul__(self, other):
		if type(other) == int:
			return EncodedMessage(self.encoding * other, rawEncoding=True)
		return EncodedMessage(self.encoding * other.encoding, rawEncoding=True) # indent?

	def __div__(self, other):
		return self.__truediv__(other)
	
	def __truediv__(self, other):
		if type(other) == int:
			return EncodedMessage(self.encoding // other, rawEncoding=True)
		return EncodedMessage(self.encoding // other.encoding, rawEncoding=True)
	
	def __eq__(self, other):
		return self.encoding == other.encoding

	def __repr__(self):
		return self.toBytes()

	def __str__(self):
		return str(self.toBytes().decode('utf-8'))
	
	def getEncoding(self):
		return self.encoding

	def fromBytes(self, bytes, addMarker = True):
		# leading with a bytearray[1] to not chop off leading 0s
		if addMarker:
			return int.from_bytes(bytearray([1]) + bytes, byteorder='big', signed=True)
		else:
			return int.from_bytes(bytearray(bytes), byteorder='big', signed=True)

	def toBytes(self, removeMarker = True):
		num_bytes = ceil(log(abs(self.encoding), 256))

		if removeMarker:
			if self.encoding < 0:
				print("ERROR: Ended with negative messages representation")
			return self.encoding.to_bytes(num_bytes, byteorder='big', signed=True)[1:] # ignore the leading 1
		else:
			try:
				return self.encoding.to_bytes(num_bytes, byteorder='big', signed=True)
			except OverflowError:
				return self.encoding.to_bytes(num_bytes + 1, byteorder='big', signed=True)


'''
	def encode(self, m):
		#start with a 1 to protect against opening characters less than 100 (like 06) have their opening 0s chopped off in long representation
		numberified = ["1"]
		for c in str(m):
			n = ord(c) #31 is the lowest meaningful ascii-- that of a space. Now the highest meaningful ascii can be represented in 2 chars (126-31)
			if n<10:
				numberified.append("00"+str(n))
			elif n<100:
				numberified.append("0"+str(n))
			else:
				numberified.append(str(n))
		return int("".join(numberified)) #in python3, int() behaves like long() from python2

	def decode(self, m):
		message = []
		threeMod = 0
		charBuffer = []
		for c in str(m)[1:]: #skip the opening '1' which is just there for messages with a first shifted character less than 10
			charBuffer.append(c)
			threeMod += 1
			if(threeMod % 3 == 0):
				message.append( chr( int("".join(charBuffer))) )
				del charBuffer[:]
		return "".join(message)
		'''

'''
messageLength = 100
message1 = []
message2 = []
message3 = []
for i in range(messageLength):
	message1.append( chr(random.randint(0,255)) )
	message2.append( chr(random.randint(0,255)) )
	message3.append( chr(random.randint(0,255)) )	

message1 = "".join(message1)
message2 = "".join(message2)
message3 = "".join(message3)

encodeStart = time.time()
message1 = AppendEncoding(message1)
message2 = AppendEncoding(message2)
message3 = AppendEncoding(message3)
encodeEnd = time.time()

addStart = time.time()
comb = message1+message2+message3
addEnd = time.time()

decodeStart = time.time()
#use str() on each to force __repr__() to be called, thus actually decoding
print str(message3)==str((comb - (message1+message2)))
decodeEnd = time.time()

print("\n{0} to encode; {1} to decode".format(encodeEnd-encodeStart, decodeEnd-decodeStart))

# print comb - (message1+message2)
'''
