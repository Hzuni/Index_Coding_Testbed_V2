import decoding, encoding, messages

class DecodeManager:
    'Handles the state info for decoding and runs decoding'

    def __init__(self, numNodes): 
        self.numNodes = numNodes
        self.reset()


    def reset(self):
        self.coeffs = []
        self.decoding_steps = []
        self.side_info = {}
        self.encoded = []

    
    def can_decode(self, msgId):
        if msgId in self.side_info:
            return True
        else:
            return False

    
    def decode_message(self, msgId):
        if msgId not in self.side_info:
            return None

        steps = self.side_info[msgId][0]
        div = self.side_info[msgId][1]

        msg = encoding.EncodedMessage(0, rawEncoding=True)

        for i in range(len(steps)):
            if steps[i] != 0:
                other = encoding.EncodedMessage(self.encoded[i], addMarker=False)
                msg = msg + (other * steps[i])

        msg = msg / div

        return msg.toBytes()

    def direct_decode(self, coeffs, steps):
        # decode what we can first
        for msgId in range(len(coeffs)):
            if (coeffs[msgId] != 0):
                if msgId in self.side_info:
                        
                    # We already have this msgId decoded, lets extract it
                    num_msgId = coeffs[msgId]
                    div = self.side_info[msgId][1]
                    steps_msgId = self.side_info[msgId][0]
                        
                    # update the orig_msg matrix
                    for i in range(len(coeffs)):
                        coeffs[i] *= div
                        coeffs[msgId] = 0
                        
                    # update the steps list
                    for i in range(len(steps)):
                        if i < len(steps_msgId):
                            steps[i] = (steps[i] * div) - (num_msgId * steps_msgId[i])
                        else:
                            steps[i] = steps[i] * div

        return coeffs, steps


    def find_new_decoded(self):
        rows_to_be_removed = []
        new_decoded = []

        for i in range(len(self.coeffs)):
            canDecode = False
            div = 0
            msgId = -1
        
            # see if this row is decodable (only one coeff)
            for j, colVal in enumerate(self.coeffs[i]):
                if canDecode and colVal != 0:
                    canDecode = False
                    break
                if not canDecode and colVal != 0:
                    canDecode = True
                    div = colVal
                    msgId = j
        
            if canDecode:
                rows_to_be_removed.append(i)
                self.side_info[msgId] = (self.decoding_steps[i], div)
                new_decoded.append(msgId)

        rows_to_be_removed.reverse()
        for row in rows_to_be_removed:
            self.coeffs.pop(row)
            self.decoding_steps.pop(row)
    
        return new_decoded


    def addMessage(self, nodes, data):
        # Nodes is the coeffs array for this message
        # Data is the actually encoded data from the message
        new_decoded = []

        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1
           
        # update th active steps
        for i in range(len(self.decoding_steps)):
            self.decoding_steps[i].append(0)

        # create our steps list
        steps = ([0] * len(self.encoded)) + [1]

        if num_coeffs > 1: # do quick decoding for side_info stuff
            # decode what we can first
            self.direct_decode(nodes, steps) 
       
        # Check the coeffs again to see if it need to be added to the matrix
        num_coeffs = 0
        for node in nodes:
            if node != 0:
                num_coeffs += 1

        if num_coeffs > 1:
                
            # Add new coeffs row
            self.coeffs.append(nodes)

            # add the new decing steps and raw_msg
            self.decoding_steps.append(steps)

            # Add a call to gauss and return a list of new decoded
            self.coeffs, self.decoding_steps = decoding.gauss(self.coeffs, self.decoding_steps)
        
        else:
            # This is a single message encoding
            for i in range(len(nodes)):
                if (nodes[i] != 0):
                    # add the elimination steps array as well as the coefficient of our single message data to be divided by at decode time
                    if i not in self.side_info:
                        self.side_info[i] = (steps, nodes[i])
                        new_decoded.append(i)
                        
                        for row in range(len(self.coeffs)):
                            self.direct_decode(self.coeffs[row], self.decoding_steps[row])
                        
            
        # Find if there is anything new for us to decode 
        new_decoded.extend(self.find_new_decoded())
        # store the original encoded combination
        self.encoded.append(data)

        return new_decoded

def test():
    # basic direct decode testing
    dh = DecodeManager(3)
    l = dh.addMessage([1,0,0],b"dfsdf")
    assert l == [0]
    l = dh.addMessage([1,1,0],b"sadf")
    assert l == [1]
    l = dh.addMessage([1,1,1],b"asdf")
    assert l == [2]
    assert len(dh.coeffs) == 0
    assert len(dh.side_info) == 3
    assert len(dh.decoding_steps) == 0

    # basic build matrix test
    dh.reset()
    l = dh.addMessage([1,1,1],b"asdf")
    assert l == []
    l = dh.addMessage([1,1,1],b"sadf")
    assert l == []
    assert len(dh.coeffs) == 2
    assert len(dh.side_info) == 0
    assert len(dh.decoding_steps) == 2

    # Circular dependency test
    dh.reset()
    m0 = encoding.EncodedMessage(b"this is a test")
    m1 = encoding.EncodedMessage(b"This is also a test")
    m2 = encoding.EncodedMessage(b"this is a third test")
    l = dh.addMessage([1,0,1], (m0 + m2).toBytes(removeMarker=False))
    assert l == []
    l = dh.addMessage([0,1,1], (m1 + m2).toBytes(removeMarker=False))
    assert l == []
    l = dh.addMessage([1,1,0], (m0 + m1).toBytes(removeMarker=False))
    assert sorted(l) == [0,1,2]
    assert dh.decode_message(0) == m0.toBytes()
    assert dh.decode_message(1) == m1.toBytes()
    assert dh.decode_message(2) == m2.toBytes()

    # non 1 values 
    dh.reset()
    mult0 = 398745987435345
    mult1 = 434534529485734
    dh.addMessage([mult0, mult1, 0], ((m0 * mult0) + (m1 * mult1)).toBytes(removeMarker=False))
    dh.addMessage([1,0,0], m0.toBytes(removeMarker=False))
    assert dh.decode_message(0) == m0.toBytes()
    assert dh.decode_message(1) == m1.toBytes()

    # Same length test. Currently fails
    dh.reset()
    m1 = encoding.EncodedMessage(b"Hello12345")
    m2 = encoding.EncodedMessage(b"arghf12345")
    m3 = m1 + m2
    l = dh.addMessage([1,1,0], m3.toBytes(removeMarker=False))
    l = dh.addMessage([1,0,0], m1.toBytes(removeMarker=False))
    assert dh.decode_message(1) == m2.toBytes()
    assert dh.decode_message(0) == m1.toBytes()

    # litle encoding test
    num = -91287398123987123712398123
    encoded = encoding.EncodedMessage(num, rawEncoding=True)
    byte_thing = encoded.toBytes(removeMarker=False)
    num2 = encoding.EncodedMessage(byte_thing, addMarker=False).encoding
    assert num == num2


    # robust testing
    decoder = DecodeManager(10)
    msgs = messages.gen_messages(10, 500)

    for experiment in range(1):
        decoder.reset()
        for msg in range(7):
            row = [0] * msg
            row.append(1)
            row.extend([0] * (10 - msg - 1))

            to_send = messages.encode_row(row, msgs, 1, 0)
            row = messages.get_coeffs(to_send, 10)
            l = decoder.addMessage(row, messages.get_data(to_send))
            assert l == [msg]
 
        row = [0, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        to_send = messages.encode_row(row, msgs, 1, 0)
        row = messages.get_coeffs(to_send, 10)
        l = decoder.addMessage(row, messages.get_data(to_send))
 
        row = [0, 1, 0, 0, 1, 0, 0, 1, 1, 0]
        to_send = messages.encode_row(row, msgs, 1, 0)
        row = messages.get_coeffs(to_send, 10)
        l = decoder.addMessage(row, messages.get_data(to_send))
        

        row = [0, -1, 0, 0, 0, 0, 0, 0, 0, -1]
        to_send = messages.encode_row(row, msgs, 1, 10)
        row_orig = row
        row = messages.get_coeffs(to_send, 10)
        assert row_orig == row

        l = decoder.addMessage(row, messages.get_data(to_send))
        
        assert l == [9]
        assert decoder.decode_message(9) == msgs[9]
    
    print("Test passed")

#test()
