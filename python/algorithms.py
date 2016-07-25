import numpy as np
import math
import messages
import random
import decoding
import copy
import time
import sys

'This is the file that contains the algorithm codes and determines with algorithm is being used'

DONT_CARE = -42
def reduceMessages(msgs, acks, tid, algo="rr"):
    new_messages = []
    coeff_size = 0
    
    #print(acks)

    if any(1 in sublist for sublist in acks):
        if algo == "rr":
            result = roundRobin(msgs, acks)
        elif algo == "ldg":
            result = LDG(acks)
        elif algo == "svdap":
            coeff_size = 50
            result = SVDAP_proxy(acks)
        else:
            print("ERROR: Unknown encoding algorithm")
            assert False
    else:
        result=[]

    for i in range(len(result)):
        msg = messages.encode_row(result[i], msgs, tid, coeff_size=coeff_size)
        if msg != None:
            new_messages.append(msg)

    return new_messages


def SVDAP_proxy(acks_orig, desired_rank=0.10):
    acks = copy.deepcopy(acks_orig)
    removed_nodes = []
    for i in range(len(acks)):
        if acks[i][i] != 1:
            removed_nodes.append(i) 

    removed_nodes.reverse()
    # remove the uneeded rows
    for node in removed_nodes:
        del acks[node]
    # remove the columns too
    for col in acks:
        for node in removed_nodes:
            del col[node]
            
    rank = np.linalg.matrix_rank(acks) 
    result = SVDAP(acks, int(desired_rank * rank))
    #print(np.array(acks))
    #print(np.array(result))
    result = decoding.gauss(result)[0]
    #print(np.array(result))
    
    # Remove the messages that are uneeded
    '''i = 0
    while i < len(result):
        zero = all(result[i][j] == 0 for j in range(len(result[i])))
        if zero:
            del result[i]
        else:
            i += 1
    '''

    # tranform back to full data set
    removed_nodes.reverse()
    for row in result:
        for node in removed_nodes:
            row.insert(node, 0)

    return result


def roundRobin(msgs, acks):
    'This method just identifies the the missing 1s along the diagnal'
    matrix = []

    for i in range(len(acks)):
        if acks[i][i] == 1:
            row = [0] * len(msgs)
            row[i] = 1
            matrix.append(row)

    return matrix


# in M, 2s are considered *. Will return a set of vectors where 1 entries should be included
def LDG(sideInfoMatrix):
    M =copy.deepcopy(sideInfoMatrix) # this shallow copies and mangles the original matrix (change to copy.deepcopy() if you want to retain sideInfoMatrix)
    i = 0
    numNodes = len(M[0])

    while i < len(M): # while we haven't gone through every row (the number of rows changes as we reduce, which is why this is not a for loop)
        rowIndices_available = set(x for x in range(len(M)) if x!=i)
        thisRow = M[i]
        mergedRow = [] # really only manipulated in the while loop, but it needs to be scoped above as to add to the index code

        # while we haven't tried to merge all rows with rowsToSelectFrom[i] but itself
        while len(rowIndices_available) > 0:
            mergeRowIndex = random.sample(rowIndices_available, 1)[0] # randomly select something to try and merge
            rowToMerge = M[mergeRowIndex]
            mergedRow = []
            # iterate through the two rows and merge, if possible
            for j in range(numNodes):
                # one is a 0 and the other is a 1; this row cannot be merged
                if thisRow[j]+rowToMerge[j] == 1:
                    rowIndices_available.remove(mergeRowIndex)
                    break
                elif thisRow[j]+rowToMerge[j] == 0:
                    mergedRow.append(0)
                # both 2s, i.e. don't cares
                elif thisRow[j]+rowToMerge[j] == 4:
                    mergedRow.append(2)
                # a don't care and a 0
                elif thisRow[j]+rowToMerge[j] == 2:
                    if thisRow[j]==rowToMerge[j]:
                        print(M, "j: ", j, "\n", thisRow, "\n", rowToMerge, "\n", mergeRowIndex, "\n", mergedRow)
                        raw_input("error \n")
                        raise BaseException("debug: somehow two 1s were merged?")
                    mergedRow.append(0)
                    didAMerge = True
                # a 1 and a don't care
                elif thisRow[j]+rowToMerge[j] == 3:
                    mergedRow.append(1)
                else:
                    print(thisRow, rowToMerge, mergedRow)
                    raw_input("error \n")
            #end for

            # if we successfully merged the row
            if len(mergedRow) == numNodes:
                M[i] = mergedRow
                M = np.delete(M,mergeRowIndex,0)
                #print("successful merge: \n", M, "\n\n")
                break

        if len(mergedRow) == numNodes:
            i = 0
        else:
            i += 1
    # end "for all rows" while loop

    for i in range(len(M)):
        for j in range(len(M[0])):
            if M[i][j] == 2:
                M[i][j] = DONT_CARE

    return np.array(M).tolist()


def APRankReduce_old(targetRank, sideInfoMatrix, eig_size_tolerance):

    iteration = 0
    n = len(sideInfoMatrix)
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")
    m = len(sideInfoMatrix[0])
    projectionDistance = 100000 # initalized to a large value
    currentRank = n

    CheckInf = 0
    M = np.random.randint(100000, size=(n,m))
    oldM = M

    while currentRank>targetRank and projectionDistance>(eig_size_tolerance/(n**3)): #and CheckInf<n-currentRank+5: #, in matlab script
        iteration += 1
        print(iteration,"\n", M)

        U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
        currentRank = 0
        for val in s:
            if val>eig_size_tolerance: currentRank += 1
        #print "rank ^", currentRank, "\n\n"
        #raw_input()
        S = np.diag(s)
        S[targetRank:, :] = 0 # killing all but targetRank many dimensions (projection onto the set of matrices with <=targetRank)
        CheckInf = S[0][0] #in matlab script

        #print "cur rank:", np.linalg.matrix_rank(M)
        M = np.dot(U, np.dot(S,V))
        #print "rank after dotting:", np.linalg.matrix_rank(M)

        projectionDistance = np.linalg.norm(oldM-M, ord=2) #L2 norm
        print( projectionDistance)
        oldM = M

        # now project back to the set of matrices where all that changed was the don't cares
        for i in range(n):
            for j in range(m):
                if sideInfoMatrix[i,j] == 1:
                    M[i,j] = 1
                elif sideInfoMatrix[i,j] == 0:
                    M[i,j] = 0
                else:
                    M[i,j] = round(M[i,j],0)
                # else, leave the calculated matrix be. Changing these values makes it possible for M to not be the original rank, yes?
    return M

# 'D' being the region where the matrix has non-zeros on the diagonal, 0s from side info set properly
def projectToD(M, sideInfoMatrix, zeroThreshold=0.0001, roundPrecision=4):
    n = len(sideInfoMatrix)
    m = len(sideInfoMatrix[0])

    for i in range(n):
        for j in range(m):
            wouldRoundTo = M[i][j]
            if roundPrecision is not None:
                wouldRoundTo = round(M[i][j], roundPrecision)

            # if we need to include it and it's been zeroed out
            if sideInfoMatrix[i][j] == 1 and (abs(M[i][j]) < zeroThreshold  or wouldRoundTo == 0):
                M[i][j] = 1 # might set this to the average of the column, or something
            elif sideInfoMatrix[i][j] == 0:
                M[i][j] = 0
            elif roundPrecision is not None:
                M[i][j] = wouldRoundTo
    return M


def thresholdRank(M, eig_size_tolerance=0.0001):
    U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
    rank = 0
    for val in s:
        if abs(val) > eig_size_tolerance: rank += 1
    return rank
    #versus #return np.linalg.matrix_rank(M)

def SVDAP(sideInfoMatrix, targetRank, startSize=10, startingMatrix=None, eig_size_tolerance=0.0001, precisionDecimals=1, max_iterations=1000, return_analysis=False):
    debug = False

    # initialization
    m = len(sideInfoMatrix[0]) # columns
    n = len(sideInfoMatrix) # rows
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")

    if startingMatrix is None:
        startingMatrix = np.random.rand(n,m)*startSize # randomly distributed large numbers
    # M is what you work with, oldM is the past iteration's M, used for calculating projection distance
    oldM = M = projectToD(startingMatrix, sideInfoMatrix, zeroThreshold=eig_size_tolerance, roundPrecision=precisionDecimals)

    projectionDistance = 9999999999 # initalized to a large value
    currentRank = thresholdRank(M, eig_size_tolerance)

    bestRank = currentRank
    bestM = M # if somehow we got to a lower rank in the projection process, we don't want to throw it out in the next projection
    bestIteration = iteration = 0

    while currentRank > targetRank  and iteration < max_iterations: #and CheckInf<n-currentRank+5: #, in matlab script and projectionDistance > eig_size_tolerance/(n**3)
        iteration += 1
        U,s,V = np.linalg.svd(M) # note that V is returned as the transpose of what matlab would return
        S = np.diag(s)
        S[targetRank:, :] = 0 # killing all but targetRank many dimensions (projection onto the set of matrices with <=targetRank)
        #CheckInf = S[0][0] #in matlab script

        M = np.dot(U, np.dot(S,V)) # reconstruct with low rank
        projectionDistance = np.linalg.norm(oldM-M, ord=2) #L2 norm
        if debug:
            pass
            #print("now rank reduced:\n", M)
            #print("with rank:", np.linalg.matrix_rank(M))
            #print(projectionDistance)

        M = projectToD(M, sideInfoMatrix, zeroThreshold=eig_size_tolerance, roundPrecision=precisionDecimals)


        oldM = M
        currentRank = thresholdRank(M, eig_size_tolerance)
        if currentRank < bestRank:
            bestM = M
            bestRank = currentRank
            bestIteration = iteration

        if debug:
            #print("now side info corrected:\n", M)
            print("side info corrected with rank:", currentRank)
            print("\n\n")
            raw_input()


    if return_analysis:
        if precisionDecimals is not None:
            M = (M*(10**precisionDecimals)).astype(int) # multiply to whole numbers and convert to integer type
            bestM = (bestM*(10**precisionDecimals)).astype(int)
        bestM = projectToD(bestM, sideInfoMatrix, roundPrecision=None)
        M = projectToD(M, sideInfoMatrix, roundPrecision=None)
        return [M.tolist(), thresholdRank(M), iteration], [bestM.tolist(), thresholdRank(bestM), bestIteration]
    else:
        if bestRank < currentRank:
            M = bestM
        #M = projectToD(M,sideInfoMatrix,roundPrecision=None)
        M = (M*(10**precisionDecimals)).astype(int) # multiply to whole numbers and convert to integer type
        return M.tolist()

def dirAP(sideInfoMatrix, targetRank, startingMatrix=None, eig_size_tolerance=0.0001, resultPrecisionDecimals=4, max_iterations=100, return_analysis=False):
    # a helper function to project to region C
    def eigenRankReduce(M, targetRank):
        eigenvalues, eigenvectors = np.linalg.eig(M)
        #eigenvalues = eigenvalues.real
        #eigenvectors = eigenvectors.real
        eigenvalues = map(lambda x : x if x>0 else 0, eigenvalues) #only positive or 0 eigenvalues (positive semi definite)
        eigenStuff = [eigenPair for eigenPair in zip(eigenvalues, eigenvectors)] # attaching each eigenvalue to it's eigenvector
        eigenStuff.sort(reverse=True, key=lambda x : x[0])  # Sort eigenpairs in ascending order according to value of eigenvector
        # overwrite the variables with the sorted stuff
        for i in range(len(eigenStuff)):
            eigenvalues[i] = eigenStuff[i][0]
            eigenvectors[i] = eigenStuff[i][1]
        for i in range(len(eigenvalues)-targetRank):
            eigenvalues[targetRank+i] = 0 # kill the least significant eigenvector directions
        eigM = np.diag(eigenvalues) # Eigenvalues of M as diagonal matrix
        return np.dot(eigenvectors, np.dot(eigM, np.transpose(eigenvectors)) )

    # initialization
    m = len(sideInfoMatrix[0]) # columns
    n = len(sideInfoMatrix) # rows
    if n==0:
        raise ValueError("sideInfoMatrix is empty!")
    if targetRank > n:
        raise ValueError("targetRank is uselessly high!")

    tmpN=[0]*60
    previousFDistanceAvg = sys.maxint # initialized to a large value
    projectionDistance = sys.maxint # initalized to a large value
    if startingMatrix is None:
        startingMatrix = np.random.rand(n,m)*9999 # randomly distributed large numbers
    M = outM = bestM = startingMatrix # AP start point
    currentRank = bestRank = thresholdRank(M, eig_size_tolerance)
    iteration = bestIteration = 0

    while(currentRank > targetRank and projectionDistance > eig_size_tolerance/n**3 and iteration < max_iterations):
        iteration += 1

        # Projection on region C
        M = eigenRankReduce(M, targetRank)

        # Projection on region D
        M = projectToD(M, sideInfoMatrix)
        OutM = M # This M maybe the optimal solution
        currentRank=np.linalg.matrix_rank(M) # Current optimal Index Code Length
        if currentRank < bestRank:
            bestM = M
            bestRank = currentRank
            bestIteration = iteration

        # Directional Projection
        M2 = M  # Second point (in region D)
        M = eigenRankReduce(M, targetRank)

        projectionDistance = np.linalg.norm(OutM-M, 2) # numpy does Frobenius norm by default, while matlab does l2
        NormF = np.linalg.norm(OutM-M2,'fro') # Frobenius distance of first and second points
        # unpacked matlab: M=OutM+NormF^2/trace((OutM-M)'*(OutM-M2))*(M-OutM);
        numerator = (OutM)
        temp1 = (NormF**2)/np.trace(np.transpose(OutM-M) *(OutM-M2)) #scalar
        if temp1 == temp1: # if temp1 is a number (not NaN)
            temp2 = temp1*(M-OutM) # back to matrix
            M = OutM + temp2 # Fourth point


        # Check stopping criteria every 60 iterations
        NumN =iteration % 60
        tmpN[NumN] = NormF
        if NumN == 60:
            ENormF=sum(tmpN)/60 # Average Frobenius distance in 60 interations
            if (iteration>60 and (previousFDistanceAvg<ENormF+eig_size_tolerance/n)):
                break
            previousFDistanceAvg=ENormF

    if bestRank < currentRank:
        outM = bestM
        currentRank = bestRank
        iteration = bestIteration
    outM = projectToD(M,sideInfoMatrix,roundPrecision=resultPrecisionDecimals)
    outM = (outM*(10**resultPrecisionDecimals)).astype(int) # multiply to whole numbers and convert to integer type

    if return_analysis:
        return outM, currentRank, iteration
    else:
        return outM

# take a matrix and add additional rows (to equal the number of columns), keeping the rank as low as possible (greedily)
def expandLDG(M, sideInfoMatrix):
    def percentNonZero(row):
        if row is None:
            return 0
        return sum(1.0 for e in row if e== DONT_CARE) / len(row)

    n = len(M) # rows
    m = len(M[0]) # cols

    # a list with a row that has that position's column nonzero, and number of nonzeros close to 50%
    # so that we can keep M's diagonal nonzero by duplicating rows whenever possible (and thus keeping rank low)
    rowWithColSet =  [None for i in range(m)]
    for i in range(n):
        for j in range(m):
            currentRowOffset = abs(0.5 - percentNonZero(M[i]))
            cachedRowOffset = abs(0.5 - percentNonZero(rowWithColSet[j]))
            if M[i][j] != 0 and currentRowOffset < cachedRowOffset:
                rowWithColSet[j] = copy.deepcopy(M[i]) # if it has the row set, and is closer to 50% nonzeros, save it

    expandedSideInfo = []
    for row in rowWithColSet:
        if row is None:
            expandedSideInfo.append([0]*m)
        else:
            expandedSideInfo.append(row)

    expandedSideInfo = projectToD(expandedSideInfo, sideInfoMatrix)
    for i in range(m):
        if expandedSideInfo[i][i] == DONT_CARE:
                expandedSideInfo[i][i] = 1

    return expandedSideInfo

def testGauss():
    '''
    A = np.eye(10)
    for i in range(len(A)):
        A[i][i] = random.randint(0,9999)
    print A, "\n", decoding.gauss(A)[0],"\n"
    '''

    A = np.array([[1,0,0,0,0,0], [0,1,0,0,0,0], [0,0,1,0,0,0], [112314,0,9991,0,0,0], [1123,9891,0,0,0,0], [91,71,81,0,0,1]])
    print(A, "\n", decoding.gauss(A)[0],"\n")


#testGauss()
