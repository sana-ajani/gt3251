import socket
import sys
import getopt
import os
import hashlib
import logging
import Packet

#create socket objects and bind to ports, send and receive data, and create connections.
class Socket:

    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.src_address = (HOST, portNum)
        self.dest_address = (HOST, portNum)
        self.seq_num = 0
        self.ack_num = 0
        self.window = 0


    #binds to socket given the host and port
    def bind_socket(ipAddress, portNum):
        try:
            self.dest_address = (ipAddress, portNum)
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
        self.socket.sendto(syn_pkt, self.dest_address)

        #wait to receive SYN ACK back
        try:
            synack, server = self.socket.recvfrom(self.window)
            #make a packet from this data
            #increment sequence number?
        except self.socket.timeout:
            logging.debug("Send SYN timeout")

    #create and send SYN ACK packet
    def send_SYNACK(self):
        synack_pkt = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, self.ack_num, [True, False, False, True, False], None)

        self.socket.sendto(synack_pkt, self.dest_address)

        try:
            ack, server = self.socket.recvfrom(self.window)
        except self.socket.timeout:
            logging.debug("Send SYN ACK timeout")

    #create and send final ACK packet
    def send_ACK(self):
        ack_pkt = create_packet(self.src_address[2], self.dest_address[2], self.seq_num, self.ack_num, [True, False, False, False, False], None)

        self.socket.sendto(ack_pkt, self.dest_address)
        try:
            data, server = self.socket.recvfrom(self.window)
        except self.socket.timeout:
            logging.debug("Send ACK timeout")
