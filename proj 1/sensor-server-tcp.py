# -*- coding: utf-8 -*-
import socket   # for sockets
import sys      # for exit
import csv
import hashlib
from datetime import datetime
import getopt
import random
import string
import logging

HOST = ''  # Symbolic name meaning all available interfaces
port = 0  # Arbitrary non-privileged port
filename = ""

allAvg = 0
allAvgCount = 0
sensorDict = {}
sensorArray = 0
dictPosition = 0

try:
   opts, args = getopt.getopt(sys.argv[1:],"q:f:d",["port=","file=", "debugging="])
except getopt.GetoptError:
   print('Using default port [' + str(port) + ']')
for opt, arg in opts:
   if opt in ("-d", "--debugging"):
      logging.basicConfig(level=logging.INFO)
   elif opt in ("-q", "--port"):
      if (arg.isdigit()):
        port = int(arg)
      else:
        logging.warning(" Port number must be a digit")
        sys.exit()
   elif opt in ("-f", "--file"):
      if ("csv" in arg):
          filename = arg
      else:
          logging.warning( " File does not exist.")
          sys.exit()

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info(" Socket Created")
except socket.error:
    logging.error(" Failed to create socket")
    sys.exit()

try:
    s.bind(('', port))
    logging.info("Socket bind complete")
except socket.error , msg:
    logging.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message: ' + msg[1])
    sys.exit()

try:
    s.listen(10)
    logging.info("Socket now listening on port [" + str(port) + "]")
except socket.error, msg:
    logging.error("Bind failed. Error Code : " + str(msg[0]) + " Message: " + msg[1])
    sys.exit()

# Now keep talking with the client
while 1:
    f = open(filename)
    reader = csv.reader(f)

    # Wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # TODO: catch exceptions here...
    authrequest = conn.recv(1024)
    if not authrequest:
        break  # Close the connection if we don't receive any data, not something you would normally allow a client to do

    # TODO: validate this data before doing anything with it...
    logging.info("Received Authentication Request [" + authrequest + "], sending challenge value")

    #generate random string
    randomString = ''.join(random.choice(string.ascii_lowercase) for i in range(64))
    # TODO catch exceptions here...
    conn.sendall(randomString)

    #reply is the concatenated string containing username + hashvalue
    reply = conn.recv(1024)
    if not reply:
        break
    clientUsername, hashvalue, sensor = reply.split(",")

    logging.info("Received the sensor username: %s and MD5 hash: %s", clientUsername, hashvalue)

    sensorvalue = int(sensor)
    row_count = 1
    checkhash = 0
    ugh = ""
    which_row = 0 #store avgCount at array[0]

    for row in reader:
        ugh = ','.join(row)
        fileUsername, password = ugh.split(",")
        row_count +=1

        if clientUsername == fileUsername:
            logging.info("Username on File and username sent by Client match. Calculating hash")
            checkhash = hashlib.md5(fileUsername + password + randomString).hexdigest()

    if checkhash == hashvalue: #auth successful

        if clientUsername in sensorDict.keys():
            dictPosition = sensorDict[clientUsername]
        else:
            which_row+=1
            sensorDict[clientUsername] = which_row
            dictPosition = which_row

        if sensorArray == 0:
            sensorArray = [[0 for x in range(row_count)] for y in range(4)]
            sensorArray[dictPosition][0] = sys.maxint
            sensorArray[dictPosition][1] = 0
            sensorArray[dictPosition][2] = 0    #sensorAvg
            sensorArray[dictPosition][3] = 0    #sensorcount

        if sensorvalue < sensorArray[dictPosition][0]:
            sensorArray[dictPosition][0] = sensorvalue
        if sensorvalue > sensorArray[dictPosition][1]:
            sensorArray[dictPosition][1] = sensorvalue

        sensorArray[dictPosition][2] = ((sensorArray[dictPosition][2] * sensorArray[dictPosition][3]) + sensorvalue) / (sensorArray[dictPosition][3] + 1)
        sensorArray[dictPosition][3]+=1

        sensorArray[0][0] = ((sensorArray[0][0] * sensorArray[0][1] + sensorvalue) / (sensorArray[0][1] + 1)) #allAverage
        sensorArray[0][1]+=1    #allCount

        sensorMin = sensorArray[dictPosition][0]
        sensorMax = sensorArray[dictPosition][1]
        sensorAvg = sensorArray[dictPosition][2]
        allAvg = sensorArray[0][0]

        conn.sendall("Sensor: " + clientUsername + " Recorded Sensor Value: " + str(sensorvalue) + " Time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                " SensorMin: " + str(sensorMin) + " SensorMax: " + str(sensorMax) + " SensorAvg : " + str(sensorAvg) + " AllAvg: " + str(allAvg))
        logging.info("Authentication was successful. Sent sensor data to Client")

    else:
        conn.sendall("User authorization failed for client: 172.0.0.4 port: " + str(port) + " user: " + clientUsername)
        logging.info("Authentication! fa")

f.close()

# TODO catch exceptions here...
conn.close()

logging.info('Connection Closed with ' + addr[0] + ':' + str(addr[1]))

# TODO catch exceptions here...
s.close()

logging.info(" Socket closed")
