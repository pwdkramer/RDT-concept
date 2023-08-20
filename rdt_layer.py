from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed
    dataReceived = ''
    nextSeqnum = 0
    cumulativeAck = 0
    countSegmentTimeouts = 0
    pipeline = 0
    outBuffer = []
    inBuffer = []

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.dataReceived = ''
        self.nextSeqnum = 0
        self.cumulativeAck = 0
        self.countSegmentTimeouts = 0
        self.pipeline = 0
        self.outBuffer = []
        self.inBuffer = []

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        # print('getDataReceived(): Complete this...')

        # ############################################################################################################ #
        return self.dataReceived

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):    

        # ############################################################################################################ #
        # print('processSend(): Complete this...')

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        # Skip this if server
        if self.dataToSend == '':
            return

        # Resend timeout packets
        tmp = []
        for (seqnum, iteration) in self.outBuffer:
            if self.currentIteration > iteration + 2:
                self.countSegmentTimeouts += 1
                segmentSend = Segment()
                data = self.dataToSend[seqnum:seqnum + self.DATA_LENGTH]
                segmentSend.setData(seqnum, data)
                print("Resending segment: ", segmentSend.to_string())
                self.sendChannel.send(segmentSend)
                iteration = self.currentIteration
            tmp.append((seqnum, iteration))
        self.outBuffer = tmp

        # Send new packets
        while self.pipeline + self.DATA_LENGTH < self.FLOW_CONTROL_WIN_SIZE:
            self.pipeline += self.DATA_LENGTH
            segmentSend = Segment()
            seqnum = self.nextSeqnum
            data = self.dataToSend[seqnum:seqnum + self.DATA_LENGTH]

            # ############################################################################################################ #
            # Display sending segment
            segmentSend.setData(seqnum,data)
            print("Sending segment: ", segmentSend.to_string())

            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(segmentSend)
            self.outBuffer.append((seqnum, self.currentIteration))
            self.nextSeqnum += self.DATA_LENGTH

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented
        # print('processReceive(): Complete this...')

        if self.dataToSend == '': # server functionality
            # Sort incase segments are out of order: https://stackoverflow.com/questions/2338531/python-sorting-a-list-of-objects
            listIncomingSegments.sort(key = lambda x: x.seqnum)


            for segment in listIncomingSegments:
                segmentAck = Segment()                  # Segment acknowledging packet(s) received

                if not segment.checkChecksum():
                    # discard segments with bad checksum. Do not send Ack
                    continue
                if segment.seqnum < self.cumulativeAck:
                    # duplicate packet. Discard.
                    acknum = self.cumulativeAck
                elif segment.seqnum == self.cumulativeAck:
                    # packet in order
                    self.cumulativeAck += self.DATA_LENGTH
                    self.dataReceived += segment.payload
                    self.inBuffer.sort(key = lambda x: x.seqnum)
                    for savedSegment in self.inBuffer:
                        if savedSegment.seqnum == self.cumulativeAck:
                            self.cumulativeAck += self.DATA_LENGTH
                            self.dataReceived += savedSegment.payload
                    tmp = [(savedSegment) for (savedSegment) in self.inBuffer if savedSegment.seqnum > self.cumulativeAck]
                    self.inBuffer = tmp
                    acknum = self.cumulativeAck
                else:
                    # packet out of order
                    self.inBuffer.append(segment)
                    acknum = self.cumulativeAck

                # Display response segment
                segmentAck.setAck(acknum)
                print("Sending ack: ", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)

        else: # client functionality, receiving Acks and removing segments from outBuffer
            listIncomingSegments.sort(key = lambda x: x.acknum)
            for segment in listIncomingSegments:
                if segment.acknum > self.cumulativeAck:
                    oldBufferSize = len(self.outBuffer)
                    # if segment.acknum - self.DATA_LENGTH in self.outBuffer:
                    #     self.outBuffer.remove(segment.acknum - self.DATA_LENGTH)
                    #     self.pipeline -= self.DATA_LENGTH
                    tmp = [(seqnum, iteration) for (seqnum, iteration) in self.outBuffer if seqnum > segment.acknum - self.DATA_LENGTH]
                    self.outBuffer = tmp
                    self.pipeline = len(self.outBuffer) * self.DATA_LENGTH
                    self.cumulativeAck = segment.acknum

        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        # print('processReceive(): Complete this...')

        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...
