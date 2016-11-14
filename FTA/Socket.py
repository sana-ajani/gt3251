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

    def send_SYN(self):
        #send SYN packet with no data and SYN flag on
        syn_pkt = create_packet(self.src_address.portNum, self.dest_address.portNum, None, None, [False, False, False, True, False], None)
        try:
            sent = self.socket.sendto(syn_pkt, self.dest_address)
