import socket
import sys
import getopt
import os
import hashlib
import logging
from Packet import Packet
import random
import pickle

#create socket objects and bind to ports, send and receive data, and create connections.
class mySocket:

    def __init__(self, HOST, portNum, isServer):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.settimeout(5)
        if (isServer):
            self.src_address = (HOST, portNum)
            self.dest_address = (0, 0)
        else:
            self.src_address = (0, 0)
            self.dest_address = (HOST, portNum)
        self.next_seq_num = 0
        self.ack_num = 0
        self.send_window_size = 1
        self.recv_window_size = 1
        self.handshake = False
        self.send_base = 0
        self.packet_array = []
        self.recv_base = 0
        self.buffer_array = [-1]*self.recv_window_size
        self.recv_data = bytearray()
        self.isDownload = False
        self.filename = ''


        print("Socket created")

    #binds to server socket given the host and port
    def bind_server_socket(self):
        try:
            self.socket.bind(self.src_address)
            print("src address", self.src_address)
        except socket.error, msg:
            logging.error(' Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1])
            sys.exit()

    def create_packet(self, src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum = None):  #delete offset
        #print("packet created")
        return Packet(src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum)

    #create and send SYN packet
    def send_SYN(self):
        #send SYN packet with no data and SYN flag on, sequence number = 0
        syn_pkt = self.create_packet(self.src_address[1], self.dest_address[1], random.randrange(0, 10), self.ack_num, [False, False, False, True, False], 0)
        #implement time out on packet
        #send SYN
        self.socket.sendto(pickle.dumps(syn_pkt), self.dest_address)
        print("sent syn by client")
        #wait to receive SYN ACK back
        try:
            synack_pkt, server_address = self.socket.recvfrom(65535)
            print("received synack by client")
            synack_pkt = pickle.loads(synack_pkt)
            self.send_ACK(synack_pkt.ack_num, synack_pkt.seq_num + 1)
            #increment sequence number?
        except socket.timeout:
            logging.debug("Send SYN timeout")

        return synack_pkt

    #create and send SYN ACK packet
    #send next_ack number that corresponds to seq #
    # src_address = server
    # dest_address = client
    def send_SYNACK(self, dest_address, next_ack):
        print dest_address
        synack_pkt = self.create_packet(self.src_address[1], dest_address[1], random.randrange(100, 200), next_ack, [True, False, False, True, False], 0)

        #send SYNACK
        #dest_address is the client's address
        self.socket.sendto(pickle.dumps(synack_pkt), dest_address)
        print("sent synack by server")
        try:
            #while synack's timer is running
            ack, client_address = self.socket.recvfrom(65535)
            ack = pickle.loads(ack)
            print "ack received by server"
        except socket.timeout:
            #send_SYNACK
            logging.debug("Send SYN ACK timeout")
            #resend limit

    #create and send final ACK packet
    # increment seq & ack b4 sending
    def send_ACK(self, next_seq, next_ack):
        ack_pkt = self.create_packet(self.src_address[1], self.dest_address[1], next_seq, next_ack, [True, False, False, False, False], 0)

        self.socket.sendto(pickle.dumps(ack_pkt), self.dest_address)
        print("sent ack")
        self.handshake = True
        #return data

    # for first SYN packet
    #called by server
    def receive_SYN(self):
        syn_pkt, client_address = self.socket.recvfrom(65535)
        print("received syn, sent synack")
        syn_pkt = pickle.loads(syn_pkt)
        self.dest_address = client_address
        self.send_SYNACK(self.dest_address, syn_pkt.seq_num + 1)

    # used by client, download
    def get_file(self, filename):

        self.isDownload = True
        download_head = "dld\x1a"
        download_byte = bytearray(download_head)
        self.send(download_byte)

        print "Download head has been sent!"


        self.filename = filename
        b = bytearray(filename)
        b.append(26)
        self.send(b)
        print "Download name sent to server!"

    # used by client, upload
    def post_file(self, fileobject, filename):
        self.isDownload = False
        upload_head = "uld\x1a"
        upload_byte = bytearray(upload_head)
        self.send(upload_byte)

        self.filename = filename
        f = fileobject.read()
        b = bytearray(f)
        b.append(26)
        self.send(b)
        print("Done. Sent all the data")
        fileobject.close()

    #client connection
    def initiate_connection(self):
        synack = self.send_SYN()

        if not synack:
            self.send_ACK()

    #server connection, used by server
    def wait_for_connect(self):
        self.receive_SYN()



    #windowSize == number of packets
    def send(self, data):
        dataChunk = None

        for i in range(0, len(data), 4):
            # print "next seq num", self.next_seq_num
            # print "send winodw size", self.send_window_size
            # print "send base", self.send_base
            if self.next_seq_num < self.send_window_size + self.send_base:
                if len(data) < 4:
                    self.sendPacket(data[i:len(data)])
                    self.listenforAck()
                else:
                    self.sendPacket(data[i:i+4])
                    if (i+4 >= len(data)):
                        self.listenforAck()
                    self.next_seq_num+=1

            else:
                while (self.next_seq_num >= self.send_window_size + self.send_base):
                    self.listenforAck()

                if len(data) < 4:
                    # print "~~~~SENDING THE RLD!!"
                    self.sendPacket(data[i:len(data)])
                    self.listenforAck()
                else:
                    #print "look for this:", data[i:i+4]
                    self.sendPacket(data[i:i+4])
                    if (i+4 >= len(data)):
                        self.listenforAck()
                    self.next_seq_num+=1



    def sendPacket(self, dataChunk):
        checksum = hashlib.md5(dataChunk).hexdigest()
        checksum = int(checksum, 32)
        #print checksum
        # print "dataChunk: ", dataChunk
        p = self.create_packet(self.src_address[1], self.dest_address[1], self.next_seq_num, self.ack_num, [False, False, False, False, False], dataChunk, checksum)
        self.packet_array.append(p)
        # print "sendpacket packet array:", p.data
        self.socket.sendto(pickle.dumps(p), self.dest_address)

    def listenforAck(self):
        # print "listening for ack"
        ack, dest_address = self.socket.recvfrom(65535)
        ack = pickle.loads(ack)
        # print "got ack from server", ack.data
        if self.verifyChecksum(ack):
            # print("Got an acknowledgement for data: ", ack.data)
            #print "ack_num throwing error,", ack.ack_num - 1
            self.packet_array[ack.ack_num - 1] = ack
            #print "send-base: ", self.send_base
            #print "listening packet array:", str(self.packet_array)
            #print "packet array at send-base", self.packet_array[self.send_base]
            while self.send_base < len(self.packet_array) and self.packet_array[self.send_base].ACK:
                self.send_base+=1
        #else:
            #wait for resend ack

    def verifyChecksum(self, packet):
        #print type(packet.data)
        # print "packet data: ", packet.data
        checksum = hashlib.md5(packet.data).hexdigest()
        checksum = int(checksum, 32)
        # print "calculated checksum: ", checksum
        # print "packet checksum: ", packet.checksum
        if checksum == packet.checksum:
            return True
        else:
            return False

    def set_client_window(self, window_size):
        self.send_window_size = window_size

    def set_server_window(self, window_size):
        self.recv_window_size = window_size

    #receiver
    def listenforPacket(self):

        packet, src_address = self.socket.recvfrom(65535)
        packet = pickle.loads(packet)
        if (packet.data == "dld\x1a"):
            self.isDownload = True
        elif (packet.data == "uld\x1a"):
            self.isDownload = False

        if (self.recv_base <= packet.seq_num and packet.seq_num <= self.recv_window_size + self.recv_base):
            # print "recvbase: ", self.recv_base
            # print "packet.seq_num: ", packet.seq_num
            # print "recv window size: ", self.recv_window_size
            if self.verifyChecksum(packet):
                p = self.sendPacketAck(packet)
                self.buffer_array[packet.seq_num] = p

                #self.recv_base+=1
                while (self.buffer_array[self.recv_base] != -1 and (self.buffer_array[self.recv_base]).ACK):
                    self.recv_data += (self.buffer_array[self.recv_base]).data
                    self.recv_base+=1
                    self.buffer_array.append(-1)


        elif ((self.recv_base - self.recv_window_size) <= packet.seq_num) and (packet.seq_num <= (self.recv_base - 1)):
            self.sendPacketAck(packet)
        #wrap around sequence numbers
        else:
            self.recv_base = 0

        if 26 in packet.data:
            return "Done"


    def sendPacketAck(self, packet):
        if packet.seq_num == 2**28 - 1:
            ack_to_send = 0
        ack_to_send = packet.seq_num + 1
        #print("ack num received", ack_to_send)
        print "packet ack data: ", packet.data
        p = self.create_packet(self.src_address[1], self.dest_address[1], packet.seq_num, ack_to_send, [True, False, False, False, False], packet.data, packet.checksum)
        self.socket.sendto(pickle.dumps(p), self.dest_address)
        print "omgggg sent"
        return p
