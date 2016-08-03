#SVD decoding scheme, needs message and reduced matrix, and test
#Author: Barak Lidsky
import numpy as np
import SVD



def SVDdec (M, Xp, row, A):
    #done on receiver side, decodes receiver's message
    N = len(M)
    #adds zeros to the end of X so it is original size
    if N > len(Xp):
        X = np.zeros((N, 1))
        for i in range(len(Xp)):
            X[i][0] = Xp[i][0]
    U, s, V = np.linalg.svd(M, full_matrices=True)
    v = np.matrix(V)
    S = np.diag(s)
    U = np.matrix(U)
    z = U[row][:]
    A = np.matrix(A)
    a = np.transpose(A)
    b = S*v*a
    message = z * (X - b)
    return (message)


def SVDenc(M, T, minRank):
    #done on transmitter side, encodes messages to send
    U, s, V = np.linalg.svd(M, full_matrices=True)
    v = np.matrix(V)
    S = np.diag(s)
    if minRank != ready(M):
        print("WARNING: MinRank doesn't match messages being sent. MinRank = ", minRank, "X' size = ", ready(M))
    X = S*v*T
    X[np.abs(X) < .001] = 0
    X = np.trim_zeros(X)
    return (X)

'''
M = np.array([(1, -1 ,0 ), (0, 1, -1), (-1, 0, 1)])
#M = np.transpose(M)

T = np.matrix([32333333, 27373762, 100287463])
T = np.transpose(T)
MSG_LEN = 10
msgs = messages.gen_messages(3, MSG_LEN)
minRank = 2
X = SVDenc(M, T, minRank)
print (X)
A = np.matrix([(0, 27373762, 0 ), (0, 0, 100287463), (32333333, 0 , 0)])
mess = []
for i in range(3):
    c = A[range(i, i + 1)]
    c = np.transpose(c)
    mess.append(SVDdec(M, X, (i + 1), c))
print (mess)
'''

def test(N):
    #test SVD decoding with APIC
    p = .3
    M = SVD.prepare(N, p)
    T = np.random.rand(N, 1)
    print(T)
    [Rmin, OptM] = SVD.APIndexCode(M)
    print(Rmin)
    X = SVDenc(OptM, T, Rmin)
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if M[i][j] > .001 and M[i][j] != 1:
                A[i][j] = T[j][0]
    message = []
    for i in range(N):
        t = SVDdec(OptM, X, i, A[i][:])
        message.append(t)
    print(message)


def ready(M):
    #receiver side; checks to see how many X' messages are needed from transmitter
    U, s, V = np.linalg.svd(M, full_matrices=True)
    S = np.diag(s)
    Index = np.nonzero(S > .001)
    size = len(Index[0])
    return size

#test(20)
def test_ready(N, p):
    #tests ready(M)
    M = SVD.prepare(N, p)
    rMin, OptM = SVD.APIndexCode(M)
    size = ready(OptM)
    print(size)

#test_ready(10, .3)