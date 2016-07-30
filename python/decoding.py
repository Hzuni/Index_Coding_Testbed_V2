__author__ = 'ryan'

from encoding import EncodedMessage
import time, errno
import copy

TIMEOUT = 10.0

# adapted from https://martin-thoma.com/solving-linear-equations-with-gaussian-elimination/
def gauss(A, decodingSteps=None):
    A = copy.deepcopy(A)
    num_rows = len(A) # rows
    num_cols = len(A[0]) # columns

    if num_rows>num_cols:
        print("more rows than columns, oh no")
        quit()

    #deoodingSteps will store the linear combination of the encoded messages needed to get to the state of a row of A
    #in a particular row of decodingSteps, the first entry represents the coefficient for the first encoded message,
    #the second entry for the second message, and so forth
    
    if decodingSteps == None:
        decodingSteps = []
        for k in range(0, num_rows):
            decodingSteps.append([0]*num_rows)
            decodingSteps[k][k] = 1 # initialize the diagonal to 1s because you start with just one of each of the encoded messages in A

    # for each row i forwards
    start_time = time.time()
    for i in range(0, num_rows):
        # Search for maximum in this column
        maxEl = abs(A[i][i])
        maxRow = i
        for k in range(i+1, num_rows):
            if abs(A[k][i]) > maxEl:
                maxEl = abs(A[k][i])
                maxRow = k

        # Swap maximum row with current row (column by column)
        for k in range(i, num_cols): #upper bound was n+1 before? even assuming a square matrix, why +1?
            tmp = A[maxRow][k]
            A[maxRow][k] = A[i][k]
            A[i][k] = tmp

        # swap the decodingSteps rows, too
        for k in range(0,num_rows):
            tmp = decodingSteps[maxRow][k]
            decodingSteps[maxRow][k] = decodingSteps[i][k]
            decodingSteps[i][k] = tmp

        # we won't be able to cancel anything with this row
        if A[i][i] == 0:
            continue

        # Make all rows below this one 0 in current column
        curRowMult = A[i][i] # doesn't change for the rows below
        for k in range(i+1, num_rows):
            if time.time() - start_time > TIMEOUT:
                raise TimeoutError("Gauss took too long")
            pivotMult = A[k][i]

            # don't reduce this row if it is already reduced
            if pivotMult == 0:
                continue
            # update all columns of the reduced row
            for j in range(i, num_cols):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] = A[k][j]*curRowMult - A[i][j]*pivotMult

            # update all columns of the decodingSteps
            for j in range(0, num_rows):
                decodingSteps[k][j] = decodingSteps[k][j]*curRowMult  -  decodingSteps[i][j]*pivotMult

    zeroedRow = []
    # reducing on the way up is slightly different, because though we want to go row by row, we want to eliminate the last column, and since
    # the matrix may not be square, we cannot use the same index variable for pivot row and column
    pivotCol = num_cols-1 # initialize this to the index of the last column
    savePivotCol = pivotCol # if we happen to have a 0 in pivotCol, keep searching to the left
    # for each row i backwards. range(start index, stop boundary, step backwards)
    for i in range(num_rows-1, -1, -1):

        # search to the left until we get
        savePivotCol = pivotCol
        while pivotCol >= 0 and A[i][pivotCol] == 0:
            pivotCol -= 1
        if pivotCol < 0:
            pivotCol = savePivotCol
            continue

        # Make all rows above this one 0 in current column
        curRowMult = A[i][pivotCol] # doesn't change for the rows above
        for k in range(i-1,-1,-1):
            if time.time() - start_time > TIMEOUT:
                raise TimeoutError("Gauss took too long")
            pivotMult = A[k][pivotCol]

            # don't reduce this row if it is already reduced
            if pivotMult == 0:
                continue
            # update all columns of the row being reduced. Cannot rely on the upper triangular property to bound which columns are added
            # since we are now reducing up the matrix. Columns don't need to be added backwards, but for conceptual continuity...
            for j in range(pivotCol, -1, -1):
                A[k][j] = A[k][j]*curRowMult - A[i][j]*pivotMult

            # update all columns of the decodingSteps
            for j in range(num_rows-1, -1, -1):
                decodingSteps[k][j] = decodingSteps[k][j]*curRowMult - decodingSteps[i][j]*pivotMult


        pivotCol = savePivotCol-1 # if we went left to find a non-zero entry, go back, and resume the normal up one left one progression

    '''
    # if we zeroed out a row, we want to move it to the bottom at the end
    for i in range(num_rows):
        if all(int(n)==0 for n in A[i]):
            zeroedRow.append(i)
    retA = []
    retSteps = []
    for i in range(num_rows):
        if i not in zeroedRow:
            retA.append(A[i])
            retSteps.append(decodingSteps[i])
    zeroedRow.reverse()
    for i in zeroedRow:
        retA.append(A[i])
        retSteps.append(decodingSteps[i])
    '''

    return A, decodingSteps

# this just works with int/long (need to adapt for data structure)
# and assumes only positive values
def efficientMult(a, b):

    def log2(n):
        if n<1:
            return None
        log = 0
        runningComparison = 1
        while True:
            if runningComparison == n:
                return log, 0
            if runningComparison > n:
                return log-1, n-(runningComparison>>1)
            runningComparison <<= 1
            log += 1
        # returns floor(log), remainder

    if a<0 or b<0:
        return None

    # want a to be the bigger
    if a < b:
        tmp = a
        a = b
        b = tmp
    orig = a
    shifts, adds = log2(b)
    print(shifts, adds)
    a <<= shifts
    for i in range(adds):
        a+=orig
    return a


# within a single round, where we recieve a set of encoded messages, decode with row reduction (assumes single pieces of side information
# already subtracted
def decodeWithRR(coefs, encodedMessages):

    reduced, steps = gauss(coefs)
    decodables = []
    for i, row in enumerate(reduced):
        canDecode = False
        divideBy = 0
        msgIndex = -1
        # if theres a single nonzero value in a row, we can decode (but have to divide in case that single value is not 1!)
        for j, columnVal in enumerate(row):
            if canDecode and columnVal != 0:
                canDecode = False
                break
            if not canDecode and columnVal != 0:
                canDecode = True
                divideBy = columnVal
                msgIndex = j

        if canDecode:
            # to decode: (index into reduced matrix, num of message you will recover, the multiple of the message you intend to recover)
            decodables.append((i,msgIndex, divideBy))

    idToMessage = {}
    for reducedRow, msg, divideBy in decodables:
        message = 0
        # eMsgNum is the index of the encoded message in the linear combination to recover the original message
        for eMsgNum, multBy in enumerate(steps[reducedRow]):
            message += encodedMessages[eMsgNum]*multBy
        # we got message to be a multiple of the intended message, now lets get the actual message
        idToMessage[msg] = message // divideBy

    return idToMessage





# row reducing by hand (especially the decodingSteps part) is a pain
def sanityCheck():
    A = [[0,2,1,-8],[1,-2,-3,0],[-1,1,2,3]]
    expectedReduced = [[1,-2,-3,0], [0,2,1,-8],[0,0,-1,-2]]
    expectedSteps = [[0,1,0],[1,0,0],[1,2,2]]
    reducedA, steps = gauss(A)
    assert(reducedA==expectedReduced)
    assert(steps==expectedSteps)



#A = [[11,20,30,40,50], [2,4,6,8,10], [1,2,3,4,5], [1,0,0,0,0]]
#print(gauss(A))
def sanityCheck2():
    msg1 = EncodedMessage(bytearray("Hello, I am message1! I'm chyah about it!", 'ascii'))
    msg2 = EncodedMessage(bytearray("Hello, I am message2! I'm ... okay about it", 'ascii'))
    msg3 = EncodedMessage(bytearray("I am not used right now", 'ascii'))
    combined1 = msg1 + msg2 + msg3
    combined2 = msg2 + msg3
    combined3 = msg3*2
    coefs = [[1,1,1],[0,1,1], [0,0,2]] # combined is 2 of msg1 and 3 of msg2, and we'll send message 2 in order to recover both
    encodedMessages = [combined1.getEncoding(), combined2.getEncoding(), combined3.getEncoding()]
    recoveredMessages = decodeWithRR(coefs,encodedMessages)
    for key in recoveredMessages :
        print(str(EncodedMessage(recoveredMessages[key], True)))

def sanityCheckRRUp():
    A = [[1,2,3,4],[0,4,6,8], [0,0,2,1]]
    reducedA, steps = gauss(A)
    print(reducedA)
    print(steps)

def testMult():
    a = 12341239487398273498273409872123908743250983245982374598324509827345987234509872345987213312398712309187233498723498723049872349872340982734987234982734
    b = 512
    start = time.time()
    r1 = a*b
    print("regular mult: ", time.time()-start)

    start = time.time()
    r2 = efficientMult(a,b) # not more efficient, oops
    print("efficient mult: ", time.time()-start)
    assert(r1==r2)

'''
A = [[1, 0, 1], [1, 1, 0], [0, 1, 1]]
eye = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
print(gauss(A, eye))
'''


#sanityCheck2()
