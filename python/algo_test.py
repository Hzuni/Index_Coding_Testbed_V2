# This is a script to test the algorithms 
#import sys, random, messages, algorithms, time
from decode_manager import DecodeManager
import encoding
import numpy as np
#import matplotlib.pyplot as plt
import copy
import pickle as pickle
#import decoding
import encoding
from decode_manager import DecodeManager
import algorithms

def originalTest():
    RUNS = 1000
    MSG_LEN = 512
    NUM_NODES = 15
    LOSS = 0.9
    ALGOS = ["rr", "ldg"]

    print("Generating messages...")

    rounds = [0] * len(ALGOS)
    sent = [0] * len(ALGOS)
    lost = [0] * len(ALGOS)
    owner_lost = [0] * len(ALGOS)

    print("Testing algorithms...")

    for algo in range(len(ALGOS)):
        rand = random.Random()
        rand.seed(123456789)

        for i in range(RUNS):
            #print("Running round", i, "...")
            acks = [[0 for x in range(NUM_NODES)] for y in range(NUM_NODES)]
            for j in range(NUM_NODES):
                acks[j][j] = 1

            msgs = messages.gen_messages(NUM_NODES, MSG_LEN)
            toSend = []
            for j in range(len(msgs)):
                toSend.append(messages.format_msg([j], msgs[j]))

            while (len(toSend) > 0):
                rounds[algo] += 1

                for msg in range(len(toSend)):
                    sent[algo] += 1
                    for node in range(NUM_NODES):
                        msg_nodes = messages.get_nodes(toSend[msg])
                        if rand.random() > LOSS:
                            lacking = 0
                            for n in msg_nodes:
                                if acks[node][n] <= 1:
                                    lacking += 1

                            if lacking <= 1:
                                for n in msg_nodes:
                                    acks[node][n] = 2;

                        else:
                            lost[algo] += 1
                            if len(msg_nodes) == 1 and msg_nodes[0] == node:
                                owner_lost[algo] += 1

                toSend = algorithms.reduceMessages(msgs, acks, ALGOS[algo])

        print("*****************************************")
        print("Algorithm:", ALGOS[algo])
        print("Avg Rounds:", rounds[algo] / RUNS)
        print("Avg Broacasts sent:", sent[algo] / RUNS)
        print("Avg Lost messages:", lost[algo] / RUNS)
        print("Avg Lost by owner:", owner_lost[algo] / RUNS)

        #print("Done.")

    print("************* Testing Done **************")


def sampleSideInfo(size, probOfDontCare):

    M = np.diag(np.ones(size))
    nonDiagEntries = 0.0
    dontCares = 0.0
    for i in range(size):
        for j in range(size):
            if i==j:
                continue # don't want to set the diagonals
            nonDiagEntries += 1
            if random.random() < probOfDontCare:
                M[i][j] = 2
                dontCares += 1

    # percentage of don't care entries, the matrix
    return (dontCares/nonDiagEntries, M)

# a square matrixSize x matrixSize
def timeSVDAP(targetRank, rounding=None, startingSize=999999999999, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    percentages = [0.05, 0.15, 0.25, 0.35, 0.55, 0.75, 0.85, 0.95]
    for probOfDontCare in percentages:
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        last, best = algorithms.SVDAP(np.array(M), targetRank, max_iterations=200, precisionDecimals=0, return_analysis=True)
        runTime = time.time() - start
        iterations = best[2]
        rankBeforeRounding = best[1]
        rankAfterRounding = algorithms.thresholdRank( algorithms.projectToD(best[0], M, roundPrecision=rounding) )
        results.append((percentDontCare, rankBeforeRounding , rankAfterRounding, iterations, runTime))

    return results

# a square matrixSize x matrixSize
def timeLDG(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        startRank = algorithms.thresholdRank(M)
        Mr = algorithms.LDG(np.array(M))
        endRank = algorithms.thresholdRank(Mr)

        runTime = time.time() - start
        results.append((percentDontCare, startRank-endRank, startRank, endRank, runTime))

    return results

def timeDirAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        start = time.time()
        Mr, rank, iterations = algorithms.dirAP(M, targetRank,resultPrecisionDecimals=8, max_iterations=200, return_analysis=True)
        runTime = time.time() - start
        results.append((percentDontCare, rank, iterations, runTime))

    return results

def timeLDGStartAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        print("start:",algorithms.thresholdRank( M))
        M = algorithms.expandLDG(algorithms.LDG(M), M)
        print("reduced/expanded:", algorithms.thresholdRank( M), "\n")
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        last, best = algorithms.SVDAP(np.array(M)*9999999999, targetRank, precisionDecimals=8, return_analysis=True)
        runTime = time.time() - start
        results.append((percentDontCare, last[1:], best[1:], runTime))

    return results

def timeLDGStartDirAP(targetRank, matrixSize=100):
    results = [] # will hold a bunch of tuples of runs of APIndexCode
    for probOfDontCare in np.arange(0, 1, 0.1):
        print(len(results))
        percentDontCare, M = sampleSideInfo(matrixSize, probOfDontCare)
        print("start:",algorithms.thresholdRank( M))
        M = algorithms.expandLDG(algorithms.LDG(M), M)
        print("reduced/expanded:", algorithms.thresholdRank( M), "\n")
        start = time.time()
        # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
        outM, rank, iterations = algorithms.dirAP(np.array(M), targetRank, startingMatrix=np.array(M)*9999999,resultPrecisionDecimals=8, return_analysis=True)
        print( rank , np.linalg.matrix_rank(M) )
        runTime = time.time() - start
        results.append((percentDontCare, rank, iterations, runTime))

    return results


def testAPYah():
    #timeAP(100)
    #recurseAP(testMatrix(100,0.3)[1], 90, 10)
    algorithms.SVDAP(sampleSideInfo(100,0.3)[1], 30, 0.001)

    timingResults = {}
    for targetRank in range(5,96, 10):
        timingResults[targetRank] = timeSVDAP(targetRank)

    xAxis = [x for x in np.arange(0, 1, 0.1)]
    width = 0.03
    for i, r in enumerate(timingResults):
        percentDontCare = []
        rank = []
        iterations = []
        runTime =[]
        for result in timingResults[r]:
            percentDontCare.append(result[0])
            rank.append(result[1])
            iterations.append(result[2])
            runTime.append(result[3])
        iterationsAxis = [x+width for x in percentDontCare]
        runTimeAxis = [x+(width*2) for x in percentDontCare]

        fig = plt.figure(i)
        rank_bars = plt.bar(percentDontCare, rank, width, color='blue', align='center')
        iter_bars = plt.bar(iterationsAxis, iterations, width, color='red', align='center')
        #time_bars = ax.bar(runTimeAxis, runTime, width, color='green')
        plt.legend((rank_bars[0],iter_bars[0]), ('Rank','Iterations'))
        plt.autoscale(tight=True)
        plt.xlabel("Percentage of side info graph DC")
        plt.yticks(np.arange(0,200,10))
        plt.title("Target Rank {}".format(r))
        fig.savefig("Small Reals/{}.png".format(r))
        plt.close(i)


def roundingTest():
    results = {}
    for targetRank in range(1, 20, 2):
        percentages = [0.05, 0.15, 0.25, 0.35, 0.55, 0.75, 0.85, 0.95]
        for probOfDontCare in percentages:
            percentDontCare, M = sampleSideInfo(20, probOfDontCare)
            start = time.time()
            # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
            last, best = algorithms.SVDAP(np.array(M), targetRank, 1, max_iterations=200, precisionDecimals=None, return_analysis=True)
            runTime = time.time() - start
            iterations = best[2]
            rankBeforeRounding = best[1]
            for rounding in [None, 8, 5, 3, 2, 1]:
                rankAfterRounding = algorithms.thresholdRank( algorithms.projectToD(best[0], M, roundPrecision=rounding) )
                results.append((percentDontCare, rounding, targetRank, rankBeforeRounding , rankAfterRounding, iterations, runTime))
    pickle.dump(results, open("roundingTest.pkl","w+"))
    for result in results:
        string = "dontCares {}\nroundingPrecision {}\ntargetRank {}\nrankBeforeRounding {}\nrankAfterRounding {}\n" \
                 "iterations {}\nruntime {}\n\n".format(result[0], result[1], result[2], result[3] , result[4], result[5], result[6])
        raw_input(string)

def initialDistributionTest():
    startSizeResults = []
    for startSize in range(12):
        timingResultsAP = []
        for targetRank in range(5,96, 10):
            timingResultsAP[targetRank] = timeSVDAP(targetRank, 10**startSize)
        startSizeResults[startSize] = timingResultsAP
    pickle.dump(startSizeResults, open("initialDistTest.pkl", "w+"))
    #startSizeResults = pickle.load(open("initialDistTest.pkl"))
    for size in startSizeResults:
        print("size ", size, ":\n")
        timingResults = startSizeResults[size]
        for targetRank in timingResults:
            print("targetRank ", targetRank, ":\n")
            raw_input(timingResults[targetRank])

def testReduction():
    times = 1
    for targetRank in [1,3, 5]:
        for probOfDontCare in [0.1, 0.2, 0.7, 0.8]:
            print("times: ", times, "\n")
            times += 1
            #print(len(results))
            percentDontCare, M = sampleSideInfo(10, probOfDontCare)
            #print("start:",algorithms.thresholdRank( M))
            M = algorithms.expandLDG(algorithms.LDG(M), M)
            #print("reduced/expanded:", algorithms.thresholdRank( M), "\n")
            start = time.time()
            # [M.tolist(), currentRank, iteration], [bestM.tolist(), bestRank, bestIteration]
            last, best = algorithms.SVDAP(np.array(M), targetRank, startSize=1, precisionDecimals=1, return_analysis=True)
            bestRank = best[1]
            bestIterations = best[2]
            # a hack to check the rank acording to gauss; since no side info has been subtracted from the matrix, decodable stuff will==rank
            gaussResult = decoding.decodeWithRR(best[0], [1]*len(best[0]))
            print( bestRank, algorithms.thresholdRank(best[0]), np.linalg.matrix_rank(M), len(gaussResult))
            runTime = time.time() - start

            print(np.array(best[0]))
            print
            print(np.array(decoding.gauss(best[0]))[0])
            print("\n")
            #print(gaussResult, "\n")
            raw_input((percentDontCare, targetRank, bestRank, len(gaussResult), runTime))

def testDecoding():
    dm = DecodeManager(6)
    sideInfo = sampleSideInfo(5, 0.8)
    m1 = encoding.EncodedMessage(b"message 1 asdf")
    m2 = encoding.EncodedMessage(b"message 2 asdf")
    m3 = encoding.EncodedMessage(b"message 3 asdf")
    m4 = encoding.EncodedMessage(b"message 4 asdf")
    m5 = encoding.EncodedMessage(b"message 5 asdf")
    messages = [m1.getEncoding(), m2.getEncoding(), m3.getEncoding(), m4.getEncoding(), m5.getEncoding()]
    encodedMessages = []
    for i, coeffs in enumerate(sideInfo):
        encodedMessage = 0
        for j, m in enumerate(messages):
            encodedMessage += (m * coeffs[j])
        encodedMessages.append(encodedMessage)

    print(encodedMessages)


    print




def testLDG():
	for i in range(0,100,10):
		percentDontCare, M = sampleSideInfo(10, i/100.0)
		print (np.linalg.matrix_rank(M), "\n\n")
		print (np.linalg.matrix_rank(algorithms.LDG(M)), "\n\n---------\n\n")
		print (np.linalg.matrix_rank(M), "\n\n")
		print (np.linalg.matrix_rank(algorithms.LDG(M)), "\n\n---------\n\n")
		raw_input()

def testLDGExpansion():
    for i in range(0,100,10):
        percentDontCare, M = sampleSideInfo(5, i/100.0)
        reducedM = algorithms.LDG(M)
        expandedM = algorithms.expandLDG(reducedM, M)
        print(M, "\n\n")
        print (np.array(reducedM), "\n\n")
        print (np.array(expandedM), "\n\n---------\n\n")

        #print np.linalg.matrix_rank(M), "\n\n"
        #print np.linalg.matrix_rank(reducedM), "\n"
        #print np.linalg.matrix_rank(expandedM), "\n\n---------\n\n"

# search over target rank, percent of side info, rounding precision, with or without LDG starting point
def gridSearchAP():

    for i in range(0,100,10):
        timingResultsAP = {}
        timingResultsLDG = {}
        timingResultsMixed = {}
        for targetRank in range(5,96, 10):
            timingResultsAP[targetRank] = timeSVDAP(targetRank)
            timingResultsLDG[targetRank] = timeLDG(targetRank)
            timingResultsMixed[targetRank] = timeLDGStartAP(targetRank)

        targetDontcare = i/100.0
        actualDontCare, M = sampleSideInfo(5, targetDontcare)
        reducedM = algorithms.LDG(M)
        expandedM = algorithms.expandLDG(reducedM, M)
        print(M, "\n\n")
        print (np.array(reducedM), "\n\n")
        print (np.array(expandedM), "\n\n---------\n\n")


#testDecoding()
#testReduction()
#roundingTest()
#initialDistributionTest()

#results = timeLDGStartDirAP(25, 50)
#for pack in results:
#    raw_input(pack)

def decodeTest():
	dm = DecodeManager(6)
	sideInfo = sampleSideInfo(6, 0.8)[1]
	m1 = encoding.EncodedMessage(b"message 1 asdf")
	m2 = encoding.EncodedMessage(b"message 2 asdf")
	m3 = encoding.EncodedMessage(b"message 3 asdf")
	m4 = encoding.EncodedMessage(b"message 4 asdf")
	m5 = encoding.EncodedMessage(b"message 5 asdf")
	m6 = encoding.EncodedMessage(b"message 6 asdf")
	messages = [m1, m2,m3,m4,m5, m6]
	encodedMessages = []
	
	for i, coeffs in enumerate(sideInfo):
		print(coeffs)
		encodedMessage = 0
		for j, m in enumerate(messages):
			encodedMessage = encodedMessage + (m * coeffs[j])
		encodedMessages.append(encodedMessage)
	decoded = None
	for i in range(len(sideInfo)):
		decoded = dm.addMessage(sideInfo[i], messages[i].toBytes(removeMarker=False))
		
		
	print(decoded)





def realData():
    sampleAcks = pickle.load(open("../experiment_data/acks.pkl","rb"))
    for ack in sampleAcks:
        toDelete = []
        for i,row in enumerate(ack):
            if row[i] == 2:
                toDelete.append(i)
        print (toDelete)

        for i in reversed(toDelete):
            del ack[i]
        for row in ack:
            for i in reversed(toDelete):
                del row[i]
        print(np.array(ack))
        curRank = algorithms.thresholdRank(ack)
        reduced = algorithms.SVDAP(ack, int(curRank/5.0), startSize=100000, precisionDecimals=8, max_iterations=1000)
        ldgRank = algorithms.thresholdRank(algorithms.LDG(ack))
        rRank = algorithms.thresholdRank(reduced)
        print ("start from:", curRank)
        print ("svdap rRank:", rRank, "\nldg rank:",ldgRank,"\n")

       	stfu = input()

realData()

#decodeTest()
#testReduction()

#testLDGExpansion()
# (sideInfoMatrix,startMatrix, targetRank, eig_size_tolerance,
#print dirAP(testMatrix(50,0.5)[1],  30)
#Mr, rank, steps = APRankReduce2(testMatrix(50, 0.5)[1], 30)
'''n=  m = 50
M = np.random.rand(20,20)
print(M)
print(np.linalg.matrix_rank(M))
Mr = np.around(M , decimals=4)
print(np.linalg.matrix_rank(np.around(M, decimals=4)))
print(Mr)'''

'''
ax = plt.subplot(111)
w = 0.3
ax.bar(x-w, y,width=w,color='b',align='center')
ax.bar(x, z,width=w,color='g',align='center')
ax.bar(x+w, k,width=w,color='r',align='center')
ax.xaxis_date()
ax.autoscale(tight=True)

plt.show()


'''



