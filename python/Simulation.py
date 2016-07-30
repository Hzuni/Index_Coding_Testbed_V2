#Simulation of Index Coding system with N nodes
#Author: Barak Lidsky
import numpy as np
import SVD
import SVD_enc

class Node:

    def __init__(self, number, tot):
        self.num = number
        self.total = tot
        self.messages = np.zeros((1, self.total))
        self.X = np.zeros((self.total, 1))
        self.M = 0
        self.mess = 0

    def get_mess(self, message, number):
        p = np.random.random()
        if (p > .5) and number != self.num:
            self.messages[0][number] = message
            return 1
        else:
            return 0

    def get_x(self, x, number):
        p = np.random.random()
        if (p > .5) :
            self.X[number][0] = x
            return 1
        else:
            return 0

    def get_M(self, M):
        p = np.random.random()
        if (p > .5):
            self.M = M.copy()
            return 1
        else:
            return 0

    def recover_mess(self):
        self.mess = SVD_enc.SVDdec(self.M, self.X, self.num, self.messages)


def simulation(N):
    #Initialize Nodes
    Nodes = []
    for i in range(N):
        Nodes.append(Node(i, N))
    #random messages
    T = np.random.rand(N, 1)
    #first round of sending messages
    M = np.zeros((N,N))
    for i in range(N):
        for j in range(N):
            temp = Nodes[j].get_mess(T[i][0], i)
            if temp == 1 and i != j:
                M[j][i] = 2
            if temp == 1 and i == j:
                M[j][i] = 1
    #APIC
    [Rmin, OptM] = SVD.APIndexCode(M)
    #SVD encoding
    X = SVD_enc.SVDenc(OptM, T, Rmin)
    #construct A, matrix of sideinfo with actual messages
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if M[i][j] == 2:
                A[i][j] = T[j][0]
    #send X and M until all receivers have them
    end = 1
    #X by N empty matrix, will fill with 1s until everyone has all of X
    U = np.zeros((len(X),N))
    #empty array, will fill with 1s until everyone has M
    G = np.zeros((1, N))
    #Init
    count = 0
    round = 0
    while(end):
        #Send all messages of X
        for i in range(len(X)):
            tem = U[i][:]
            left = np.nonzero(tem == 0)
            #If everyone has X message, don't resend it
            if len(left[0]) > 0:
                count += 1
                for j in range(N):
                    if Nodes[j].X[i][0] == 0:
                        temp = Nodes[j].get_x(X[i][0], i)
                        if temp == 1:
                            U[i][j] = 1
        #Send M to everyone
        numleft = np.nonzero(G == 0)
        #If everyone has M, don't resend it
        if len(numleft[0]) > 0:
            count += 1
            for i in range(N):
                if G[0][i] == 0:
                    temp = Nodes[i].get_M(OptM)
                    if temp == 1:
                        G[0][i] = 1
        #increment round
        round +=1
        zeros = np.nonzero(U == 0)
        #If everyone has all the messages, exit while loop of sending
        if len(zeros[0]) == 0 and len(numleft[0]) == 0:
            end = 0

    for i in range(N):
        #nodes recover their messages
        Nodes[i].recover_mess()

    #check results
    for i in range(N):
        print(i)
        print("rec: ", Nodes[i].mess, "t: ", T[i][0], "diff: ", abs(Nodes[i].mess - T[i][0]))
    print("Rounds: ", round, "count: ", count, "N: ", N, "Rmin: ", Rmin)


simulation(14)