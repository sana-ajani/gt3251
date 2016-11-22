import socket
import sys
import getopt
import os
import hashlib
import logging
import Packet
import random
from timeout import timeout
#http://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
#lol

#create socket objects and bind to ports, send and receive data, and create connections.
class Socket:

    def __init__(self, HOST, portNum, isServer):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if (isServer):
            self.src_address = (HOST, portNum)
            self.dest_address = (0, 0)
        else:
            self.src_address = (0, 0)
            self.dest_address = (HOST, portNum)
        self.seq_num = randrange(0, 10)
        self.ack_num = 0
        self.window = 0

        self.handshake = False

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
        syn_pkt = create_packet(self.src_address[1], self.dest_address[1], self.seq_num, self.ack_num, [False, False, False, True, False], None)

        #implement time out on packet
        #send SYN
        self.socket.sendto(syn_pkt, self.dest_address)

        #wait to receive SYN ACK back
        try:
            synack, server_address = self.socket.recvfrom(65535)
            #increment sequence number?
        except self.socket.timeout:
            logging.debug("Send SYN timeout")

        return synack

    #create and send SYN ACK packet
    #send next_ack number that corresponds to seq #
    # src_address = server
    # dest_address = client
    def send_SYNACK(self, dest_address, next_ack):

        synack_pkt = create_packet(self.src_address[1], dest_address[1], self.seq_num, next_ack, [True, False, False, True, False], None)

        #send SYNACK
        #dest_address is the client's address
        self.socket.sendto(synack_pkt, dest_address)

        try:
            #while synack's timer is running
            ack, client_address = self.socket.recvfrom(65535)
        except self.socket.timeout:
            #send_SYNACK
            logging.debug("Send SYN ACK timeout")
            #resend limit

        return ack

    #create and send final ACK packet
    # increment seq & ack b4 sending
    def send_ACK(next_seq, next_ack):
        ack_pkt = create_packet(self.src_address[1], self.dest_address[1], next_seq, next_ack, [True, False, False, False, False], None)

        self.socket.sendto(ack_pkt, self.server_address)

        try:
            data, server = self.socket.recvfrom(65535)
        except self.socket.timeout:
            logging.debug("Send ACK timeout")

        self.handshake = True
        #return data


    # for first SYN packet
    #called by server
    def receive_SYN(self):
        syn_pkt, client_address = self.socket.recvfrom(65535)
        self.dest_address = client_address
        send_SYNACK(self.dest_address[1], syn_pkt.seq_num + 1)


    def receive_SYNACK(self):
        synack_pkt, server_address = self.socket.recvfrom(65535)
        send_ACK(synack_pkt.ack_num, synack_pkt.seq_num + 1)




    def get_file(self, filename):
        f = open


    def post_file(self, fileobject):
        return



    #client connection
    def initiate_connection():
        synack = self.send_SYN()

        if not synack:
            self.send_ACK()

    #server connection
    def wait_for_connect(self):
        return


    #send data
    #windowSize == number of packets
    def send(self, data, windowSize):

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
            p = create_packet(src_address[1], self.dest_address[1], self.seq_num, self.ack_num, [False, False, False, False, False], data, checksum)
            self.seq_num+=1
            packetQueue.append(p)

        #keep track of packets sent, but not acknowledged
        sentQueue = queue()

        #send packets until sendWindowSize = 0
        while windowSize > 0:
            packetToSend = packetQueue.dequeue()
            self.sendto(packetToSend, self.dest_address)
            print("sent packet to server")
            windowSize -= 1
            sentQueue.append(packetToSend)

        #wait for ack for packets in order to move window size
        #try:
            #print("waiting for ack")

#change window size method

#recevive method
