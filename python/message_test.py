import numpy as np
import struct


def matrix_receiver(msg_received):	
	if msg_received[0] == ord('m'):
		rows = msg_received[1]
		print("the number of rows is", rows)
		columns = msg_received[2]
		print("the number of columns is", columns)
		m = np.zeros((rows, columns))

		for i in range(0, rows):
			for j in range(0, columns):
				m_ij_bytes = bytearray()
				for k in range(0, 8):
					byte_k = ( (i * columns * 8) + (j*8) + k+ 3)
					m_ij_bytes.append(msg_received[byte_k])
				recv_dbl = struct.unpack("d",m_ij_bytes)	
				m[i][j] = recv_dbl[0]
		print(m)
