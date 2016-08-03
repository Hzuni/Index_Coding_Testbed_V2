#[Rmin,OptM] = APIndexCoding(M)
#Author: Barak Lidsky
import numpy as np
from numpy import linalg as LA

def APIndexCode(M):
    N = len(M)
    #Main structure of algo
    Rmin = N
    Rnk = N
    [OneIndex, ZeroIndex] = getVals(M)
    [exi, OutM, Rnk] = dirSVDAP(Rmin, N, OneIndex, ZeroIndex, Rnk)
    while (exi):
        Rmin = Rmin - 1
        OptM = OutM.copy()
        [exi, OutM, Rnk] = dirSVDAP(Rmin, N, OneIndex, ZeroIndex, Rnk)
    Rmin = Rmin + 1
    #Rmin = Rmin / b
    return (Rmin, OptM)


def dirSVDAP(r, N, OneIndex, ZeroIndex, Rnk):
    #DIRSVDAP code, works best for square non-symmetrical matrices
    #Initializations
    Ite = 0
    CheckInf = 0
    DisM = 1
    M = np.random.rand(N,N)
    for i in range(len(OneIndex[1])):
        M[OneIndex[0][i]][OneIndex[1][i]] = 1
    for i in range(len(ZeroIndex[1])):
        M[ZeroIndex[0][i]][ZeroIndex[1][i]] = 0
    #M(OneIndex) = 1
    OutM = M.copy()
    tmpN = np.zeros((1, 60))
    while (Rnk > r and DisM > (.001)/(N**3) and CheckInf < (N - Rnk + 5)):
        Ite = 1 + Ite
        #print(Ite)
        U, S, V = np.linalg.svd(M, full_matrices=True)
        S = np.diag(S)
        place = N - 1
        for i in range(N - r):
            S[place][place] = 0
            place = place - 1
        M = (U.dot(S)).dot(V)
        DisM = np.linalg.norm(OutM - M)
        OutM = M.copy()
        for i in range(len(OneIndex[1])):
            M[OneIndex[0][i]][OneIndex[1][i]] = 1
        for i in range(len(ZeroIndex[1])):
            M[ZeroIndex[0][i]][ZeroIndex[1][i]] = 0
        M2 = M.copy()
        U, S, V = np.linalg.svd(M, full_matrices=True)
        S = np.diag(S)
        Rnk = len((np.nonzero(S > 0.001)[1]))
        place = N - 1
        for i in range(N - r):
            S[place][place] = 0
            place = place - 1
        CheckInf = S[0][0]
        #print(CheckInf)
        #print(Rnk)
        #print(r)
        M = (U.dot(S)).dot(V)
        NormF = LA.norm(OutM - M2, 'fro')
        #M = OutM.copy()
        Hey = NormF**2
        ho = OutM - M
        What = np.transpose(ho)
        um = OutM - M2
        Wat = What.dot(um)
        sup = np.trace(Wat)
        W = Hey/sup
        Y = W*(M - OutM)
        M = OutM + Y
        #M = M + (NormF**2)/np.trace((np.transpose(OutM - M)).dot(OutM - M2))
        #M = M.dot(M - OutM)
        NumN = ((Ite - 1) % 60) + 1
        tmpN[0][NumN - 1] = NormF
        if (NumN == 60):
            ENormF = np.sum(tmpN) / 60
            if (Ite > 60 and (tmpF < ENormF or (abs(tmpF - ENormF) < (0.001/N)))):
                DisM = 0
            tmpF = ENormF
        for i in range(len(OneIndex[1])):
            M[OneIndex[0][i]][OneIndex[1][i]] = 1
        for i in range(len(ZeroIndex[1])):
            M[ZeroIndex[0][i]][ZeroIndex[1][i]] = 0
    exi = (Rnk <= r) & (CheckInf < (N - Rnk + 5))
    return (exi, OutM, Rnk)


def getVals(M):
    #Produce indices of Ones and Zeros of given Matrix
    tol = 0.1**3
    n = 0
    m = 0
    [n, m] = np.shape(M)
    for i in range(len(M)):
        M[i][i] = 1
    OneIndex = np.nonzero(M==1)
    ZeroIndex = np.nonzero(M==0)
    return (OneIndex, ZeroIndex)

def reduce(acks):
    #Reduce side info of matrix with p chance of keeping the message
    #If the connection between transmitter and receiver is too good, use this
    Index = np.nonzero(acks == 2)
    N = len(acks)
    Total = N*N - N
    if len(Index[0])/Total > .5 :
        p = .3
        G = np.random.rand(N,N)
        for i in range(N):
            for j in range(N):
                if G[i][j] < (1 - p) and i != j:
                    acks[i][j] = 0
    return acks


def prepare(N, p):
    #Produce a P probability random Matrix with size N
    M = np.random.rand(N, N)
    for i in range(N):
        for j in range(N):
            if M[i][j] < (1 - p) :
                M[i][j] = 0
            else:
                M[i][j] = 2
            if i == j:
                M[i][j] = 1
    return M
'''
M = np.array([(1, 0 ,0 ), (0, 1, -1), (-1, 0, 1)])
[OneIndex, ZeroIndex] = getVals(M)
print(OneIndex)
size = len(OneIndex[1])
hey = OneIndex[1][1]
print (size)
'''

def test():
    #Test APIndex Algo with different P 100 times each
    P = [.1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7]
    iter = 100
    size = 8
    avgRank = []
    for prob in P:
        sumRmin = 0
        for i in range(iter):
            print(i)
            M = prepare(size, prob)
            # print (M)
            rMin, OptM = APIndexCode(M)
            sumRmin = sumRmin + rMin
        avgRank.append(sumRmin/iter)
        print (avgRank)


def singletest(N, p):
    #tests APIC once with size and probability
    M = prepare(N, p)
    rMin, OptM = APIndexCode(M)
    print(rMin)

#singletest(10, .1)
#test()
'''
M = prepare(10, .7)
print(M)
G = reduce(M)
print (G)
'''