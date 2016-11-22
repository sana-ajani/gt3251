import socket
import sys
import getopt
import os
import hashlib
import logging
import Packet
from timeout import timeout
#http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish

#create socket objects and bind to ports, send and receive data, and create connections.
class Socket:

    def __init__(self, HOST, portNum):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (HOST, portNum)
        #self.seq_num = 0
        #self.ack_num = 0
        self.window = 0


    #binds to server socket given the host and port
    def bind_server_socket(HOST, portNum):
        try:
            self.server_address = (HOST, portNum)
            self.socket.bind(dest_address)
        except socket.error, msg:
            logging.error(' Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1])
            sys.exit()


    def create_packet(src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum = None):  #delete offset
        return Packet(src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum)

    #create and send SYN packet
    def send_SYN(self):
        #send SYN packet with no data and SYN flag on, sequence number = 0
        syn_pkt = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, None, [False, False, False, True, False], None)

        #implement time out on packet
        #send SYN
        self.socket.sendto(syn_pkt, self.server_address)

        #wait to receive SYN ACK back
        try:
            synack, server = self.socket.recvfrom(65535)
            #increment sequence number?
        except self.socket.timeout:
            logging.debug("Send SYN timeout")

        return synack

    #create and send SYN ACK packet
    def send_SYNACK(self):
        
        synack_pkt = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, self.ack_num, [True, False, False, True, False], None)

        self.socket.sendto(synack_pkt, self.dest_address)

        try:
            #while synack's timer is running
            ack, server = self.socket.recvfrom(self.window)
        except self.socket.timeout:
            #send_SYNACK
            logging.debug("Send SYN ACK timeout")
            #return none to client
            #resend limit


    #create and send final ACK packet
    def send_ACK(self):
        ack_pkt = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, self.ack_num, [True, False, False, False, False], None, None)

        self.socket.sendto(ack_pkt, self.dest_address)
        try:
            data, server = self.socket.recvfrom(self.window)
        except self.socket.timeout:
            logging.debug("Send ACK timeout")

    #client connection
    def initiate_connection():
        synack = self.send_SYN()

        if !synack:
            self.send_ACK()


    #server connection
    def wait_for_connect(self):



    #send data
    def send(self, data, sendWindowSize):

        #append data into queue in chunks
        dataQueue = queue()

        for i in range(0, len(data), 4):
            if len(data) < 4:
                dataQueue.append(data[i:i+len(data)])
            else:
                dataQueue.append(data[i:i+4])

        #create packets from those chunks of data, create header for each packet
        packetQueue = queue()

        for data in dataQueue:
            checksum = hashlib.md5(data).hexdigest()
            p = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, self.ack_num, [False, False, False, False, False], data, checksum)
            self.seq_num+=1
            packetQueue.append(p)

        #keep track of packets sent, but not acknowledged
        sentQueue = queue()

        #send packets until sendWindowSize = 0
        while sendWindowSize > 0:
            packetToSend = packetQueue.dequeue()
            self.sendto(packetToSend, self.dest_address)
            print("sent packet to server")
            sendWindowSize -= 1
            sentQueue.append(packetToSend)

        #wait for ack for packets in order to move window size
        try:
            print("waiting for ack")
            d


#change window size method
