import socket
import sys
import csv
import hashlib
from datetime import datetime
import getopt
import random
import string
import logging
import os

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
       if "csv" in arg:
           filename = arg
       else:
           logging.warning( " File does not exist.")
           sys.exit()

# Create a UDP/IP socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    logging.info(" Socket Created")
except socket.err, msg:
    logging.error('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

server_address = (HOST, port)
logging.info(" Binding socket to the port")

try:
    sock.bind(server_address)
    logging.info(' Bind complete: started on %s port %s' % server_address)
except socket.error, msg:
    logging.error(' Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1])
    sys.exit()

while True:
    logging.info("Waiting to receive message from client")
    data, address = sock.recvfrom(4096)
    state, restOfMessage = data.split("|")

    if (state == "0"): #state 0 authrequest
        logging.info("Received Authentication Request [" + restOfMessage + "] from" + str(address))
        randomString = ''.join(random.choice(string.ascii_lowercase) for i in range(64))

        sent = sock.sendto(randomString, address)
        logging.info("SENT Challenge value back")

    elif (state == "1"):
        clientUsername, hashvalue, sensor = restOfMessage.split(",")
        logging.info("Received the sensor username: %s and MD5 hash: %s from address: %s ", clientUsername, hashvalue, address)

        try:
            sensorvalue = int(sensor)
        except ValueError:
            logging.error("Please pass in a correct value for the sensor")
            sys.exit()

        row_count = 1
        checkhash = 0
        ugh = ""
        which_row = 0 #store avgCount at array[0]

        f = open(filename)
        reader = csv.reader(f)

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


            sent = sock.sendto(("Sensor: " + clientUsername + " Recorded: " + str(sensorvalue) + " Time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                    " SensorMin: " + str(sensorMin) + " SensorMax: " + str(sensorMax) + " SensorAvg : " + str(sensorAvg) + " AllAvg: " + str(allAvg)), address)
            logging.info("Authentication was successful. Sent sensor data to Client")

        else:
            sent = sock.sendto(("User authorization failed for Client: 172.0.0.4 port: " + str(port) + " \n User: " + clientUsername + "Time:" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')), address)
            logging.info("Authentication! fa")
