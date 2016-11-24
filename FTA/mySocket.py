import socket
import sys
import getopt
import os
import hashlib
import logging
from Packet import Packet
import random
import pickle
import time
# import signal

import multiprocessing

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
        self.timestamps = [-1]*self.send_window_size
        self.isConnected = False

        #index of packet in timestamps that timed out
        self.timed_out_index = -1
        logging.info(" Socket created")

    #called after get and post on both server and client
    def reset(self):
        self.next_seq_num = 0
        self.ack_num = 0
        self.send_base = 0
        self.packet_array = []
        self.recv_base = 0
        self.buffer_array = [-1]*self.recv_window_size
        self.recv_data = bytearray()
        self.timestamps = [-1]*self.send_window_size

    #binds to server socket given the host and port
    def bind_server_socket(self):
        try:
            self.socket.bind(self.src_address)
            #logging.info(self.src_address)
        except socket.error, msg:
            logging.error(' Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1])
            sys.exit()

    def create_packet(self, src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum = None):  #delete offset
        return Packet(src_portNum, dest_portNum, seq_num, ack_num, flags, data, checksum)

    #create and send SYN packet with no data and SYN flag on,
    def send_SYN(self):
        syn_pkt = self.create_packet(self.src_address[1], self.dest_address[1], random.randrange(0, 10), self.ack_num, [False, False, False, True, False], 0)
        self.socket.sendto(pickle.dumps(syn_pkt), self.dest_address)
        #try to receive SYN ACK back
        try:
            synack_pkt, server_address = self.socket.recvfrom(65535)
            logging.info(" Received SYNACK")
            synack_pkt = pickle.loads(synack_pkt)
            #ACK sent back increments sequence number
            self.send_ACK(synack_pkt.ack_num, synack_pkt.seq_num + 1)
        except socket.timeout:
            logging.debug("Send SYN timeout")

        return synack_pkt

    # create and send SYN ACK packet
    # send next_ack number that corresponds to seq #
    # src_address = server
    # dest_address = client
    def send_SYNACK(self, dest_address, next_ack):
        logging.info(" Sending to destination address at {0}".format(dest_address))
        synack_pkt = self.create_packet(self.src_address[1], dest_address[1], random.randrange(100, 200), next_ack, [True, False, False, True, False], 0)
        self.socket.sendto(pickle.dumps(synack_pkt), dest_address)
        logging.info(" Sent SYNACK")
        try:
            ack, client_address = self.socket.recvfrom(65535)
            ack = pickle.loads(ack)
            logging.info(" Received ACK")
        except socket.timeout:
            logging.debug("Send SYN ACK timeout")

    #create and send final ACK packet
    #increment seq & ack before sending
    def send_ACK(self, next_seq, next_ack):
        ack_pkt = self.create_packet(self.src_address[1], self.dest_address[1], next_seq, next_ack, [True, False, False, False, False], 0)
        self.socket.sendto(pickle.dumps(ack_pkt), self.dest_address)
        logging.info(" Sent ACK")
        self.handshake = True

    #for first SYN packet in handshake
    #called by server
    def receive_SYN(self):
        syn_pkt, client_address = self.socket.recvfrom(65535)
        logging.info(" Received SYN")
        syn_pkt = pickle.loads(syn_pkt)
        self.dest_address = client_address
        self.send_SYNACK(self.dest_address, syn_pkt.seq_num + 1)

    # used by client, download
    def get_file(self, filename):
        self.isDownload = True
        download_head = "dnld"

        self.filename = filename
        b = bytearray(download_head + filename)
        b.append(26)
        self.send(b)
        self.reset()
        logging.info(" FILE NAME TO DOWNLOAD SENT TO SERVER!")

    # used by client, upload
    def post_file(self, fileobject, filename):
        self.isDownload = False
        upload_head = "upld"

        self.filename = filename
        f = fileobject.read()
        b1 = bytearray(upload_head)
        b2 = bytearray(filename)

        b2.insert(0, 2)
        b2.append(3)

        b3 = bytearray(f)
        b4 = b1 + b2 + b3

        b4.append(26)
        self.reset()
        self.send(b4)
        logging.info(" Done. Sent all the data")
        fileobject.close()

    #client connection
    def initiate_connection(self):
        synack = self.send_SYN()

        if not synack:
            self.send_ACK()

    #server connection, used by server
    def wait_for_connect(self):
        self.receive_SYN()

    def change_window(self, window_size):
        self.send_window_size = window_size
        self.recv_window_size = window_size
        # self.buffer_array = window_size

        difference_buffer_window = window_size - len(self.buffer_array)
        for i in range(difference_buffer_window):
            self.buffer_array.append(-1)

        difference_time_window = window_size - len(self.timestamps)
        for i in range(difference_time_window):
            self.timestamps.append(-1)

    # checks the time of timed out packets
    def check_time(self):
        for i in range(len(self.timestamps)):
            if time.time() - self.timestamps[i] > 2:
                return i
        return -1

    def handler(self):
        self.timed_out_index = self.check_time()

    def listenforAckHelperNonTerminate(self):
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=self.listenforAck, args=(self.send_base,queue))
        p.start()

        # Wait for 2 seconds or until process finishes and quits
        p.join(2)
        self.send_base = queue.get()
        print "changed send_base", self.send_base
        if (self.next_seq_num >= self.send_window_size + self.send_base):
            self.listenforAckHelper()

        if p.is_alive():
            print "running... let's kill it..."
            self.handler()
            if self.timed_out_index != -1:
                resend_seq_num = self.timed_out_index + self.send_base
                packet_resend_data = self.packet_array[resend_seq_num].data
                self.sendPacket(packet_resend_data, True)
                self.timed_out_index = -1
                self.timestamps[self.timed_out_index] = time.time()
            # Terminate
            p.terminate()
            p.join()
            self.listenforAckHelper()

        return None

    def listenforAckHelper(self):
        queue = multiprocessing.Queue()

        p = multiprocessing.Process(target=self.listenforAck, args=(self.send_base,queue))
        p.start()

        # Wait for 2 seconds or until process finishes and quits
        p.join(2)
        self.send_base = queue.get()

        if (self.send_base != len(self.packet_array)):
            self.listenforAckHelper()

        # If thread is still active
        if p.is_alive():
            print "running... let's kill it..."
            self.handler()
            if self.timed_out_index != -1:
                resend_seq_num = self.timed_out_index + self.send_base
                packet_resend_data = self.packet_array[resend_seq_num].data
                self.sendPacket(packet_resend_data, True)
                self.timed_out_index = -1
                self.timestamps[self.timed_out_index] = time.time()
            # Terminate
            p.terminate()
            p.join()
            self.listenforAckHelper()

        return None


    #windowSize == number of packets
    def send(self, data):
        dataChunk = None

        for i in range(0, len(data), 4):
            # print "next seq num", self.next_seq_num
            # print "send winodw size", self.send_window_size
            # print "send base", self.send_base
            if self.next_seq_num < self.send_window_size + self.send_base:
                if len(data) - i < 4:
                    self.sendPacket(data[i:len(data)], False)
                    if (self.send_base != len(self.packet_array)):
                        self.listenforAckHelper()

                else:
                    self.sendPacket(data[i:i+4], False)
                    self.next_seq_num+=1
                    if (i+4 == len(data)):
                        if self.send_base != len(self.packet_array):
                            self.listenforAckHelper()

            else:
                if (self.next_seq_num >= self.send_window_size + self.send_base):

                    # Start bar as a process
                    self.listenforAckHelper()

                if len(data) - i < 4:
                    self.sendPacket(data[i:len(data)], False)
                    if self.send_base != len(self.packet_array):

                        #check timestamps after 2 secs if listenforAck doesn't finish
                        self.listenforAckHelper()
                else:
                    #print "look for this:", data[i:i+4]
                    self.sendPacket(data[i:i+4], False)
                    self.next_seq_num+=1
                    if (i+4 == len(data)):
                        if self.send_base != len(self.packet_array):

                            self.listenforAckHelper()

    def sendPacket(self, dataChunk, isDup):

        checksum = hashlib.md5(dataChunk).hexdigest()
        checksum = int(checksum, 32)
        #print checksum
        # print "dataChunk: ", dataChunk
        p = self.create_packet(self.src_address[1], self.dest_address[1], self.next_seq_num, self.ack_num, [False, False, False, False, False], dataChunk, checksum)
        self.packet_array.append(p)
        # print "sendpacket packet array:", p.data
        self.socket.sendto(pickle.dumps(p), self.dest_address)
        # print "Sent packet:", p.data
        if not isDup:
            index_time = self.next_seq_num - self.send_base
            # print "This is the index for the time:", index_time
            # print "Time array size:", len(self.timestamps)
            self.timestamps[index_time] = time.time()

    def listenforFin(self):
        ack, dest_address = self.socket.recvfrom(65535)
        ack = pickle.loads(ack)
        logging.info(" Received ACK for packet with data: {0}".format(ack.data))

        if (ack.FIN == 1):
            logging.info(" Sending FINACK")
            self.send_FINACK(ack)

    def listenforAck(self, send_base, queue):
        ack, dest_address = self.socket.recvfrom(65535)
        ack = pickle.loads(ack)
        logging.info(" Received ACK for packet with data: {0}".format(ack.data))

        if self.verifyChecksum(ack):
            self.packet_array[ack.ack_num - 1] = ack
            while send_base < len(self.packet_array) and self.packet_array[send_base].ACK:
                send_base+=1
            queue.put(send_base)

    # checksum is 32 bits of an MD5 hash
    # verifies if checksum in header is same as checksum calculated on data
    def verifyChecksum(self, packet):
        checksum = hashlib.md5(packet.data).hexdigest()
        checksum = int(checksum, 32)
        if checksum == packet.checksum:
            logging.info(" Checksum is verified")
            return True
        else:
            return False

    # receiver will be listening for packets, detect if upload or download
    # receiver will check if packet is within receiving window size, check the checksum, and add to bufferarray
    def listenforPacket(self):

        packet, src_address = self.socket.recvfrom(65535)
        packet = pickle.loads(packet)
        # handling duplicates
        if self.recv_base > packet.seq_num:
            self.sendPacketAck(packet)
            return None

        if (packet.data == "dnld"):
            self.isDownload = True
        elif (packet.data == "upld"):
            self.isDownload = False

        if (packet.FIN):
            self.send_FINACK(packet)

        if (self.recv_base <= packet.seq_num and packet.seq_num <= self.recv_window_size + self.recv_base):
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
        #26 = end of file
        if 26 in packet.data:
            return "Done"

    #sends an acknowledgement on the @param packet with ACK flag and ACK num incremented
    def sendPacketAck(self, packet):
        if packet.seq_num == 2**28 - 1:
            ack_to_send = 0
        ack_to_send = packet.seq_num + 1
        p = self.create_packet(self.src_address[1], self.dest_address[1], packet.seq_num, ack_to_send, [True, False, False, False, False], packet.data, packet.checksum)
        self.socket.sendto(pickle.dumps(p), self.dest_address)
        logging.info(" Sent an ACK for the packet with data {0}".format(p.data))
        return p

    #send FIN packet with no data and FIN flag
    def send_FIN(self):
        empty_bytearray = bytearray()
        fin_pkt = self.create_packet(self.src_address[1], self.dest_address[1], random.randrange(0, 10), self.ack_num, [False, False, False, False, True], empty_bytearray)
        self.socket.sendto(pickle.dumps(fin_pkt), self.dest_address)

        #wait to receive FINACK
        finack_pkt, server_address = self.socket.recvfrom(65535)
        finack_pkt = pickle.loads(finack_pkt)
        if (finack_pkt.ack_num == fin_pkt.ack_num + 1):

            #wait for timeout, then close
            self.socket.settimeout(5)
            try:
                while True:
                    self.listenforFin()
            except socket.timeout:
                self.socket.close()
                logging.info(" Socket closed")

    #send FINACK with ACK number = FIN + 1
    def send_FINACK(self, fin):
        finack_pkt = self.create_packet(self.src_address[1], self.dest_address[1], random.randrange(0, 10), fin.ack_num + 1, [False, False, False, False, True], fin.data)
        self.socket.sendto(pickle.dumps(finack_pkt), self.dest_address)
        logging.info(" Sent FINACK")
