import socket
import sys
import getopt
import os
import hashlib
import logging

server = 'localhost';
port = 0;
username = "";
password = "";
sensorvalue = "";
authrequest = "authrequest"
debug = "";
totalAttempts = 10
state = "0"
found_arg = [1] * 5


try:
   opts, args = getopt.getopt(sys.argv[1:],"s:p:u:c:r:d",["server=","port=","username=", "password=", "sensorvalue=", "debugging="])
except getopt.GetoptError:
   print 'using default server [' + server + ']'

for opt, arg in opts:
   if opt in ("-d", "--debugging"):
       logging.basicConfig(level=logging.INFO)
   elif opt in ("-s", "--server"):
       for char in arg:
           #check if ip address is all numbers and .
           if (char.isdigit() or char == "."):
                check = True
           else:
                check = False
       if (check):
         server = arg
         found_arg[0] = 0 #this argument is present
       else:
         logging.warning(" Please input a correct IP address")
         sys.exit()
   elif opt in ("-p", "--port"):
      if (arg.isdigit()):
        port = int(arg)
        found_arg[1] = 0
      else:
          logging.warning(" Port number must be a digit")
          sys.exit()
   elif opt in ("-u", "--username"):
       username = arg
       found_arg[2] = 0
   elif opt in ("-c", "--password"):
       password = arg
       found_arg[3] = 0
   elif opt in ("-r", "--sensorvalue"):
       if (arg.isdigit()):
           sensorvalue = int(arg)
           found_arg[4] = 0
       else:
        logging.warning(" Bad Data")

#check if all args are present
if (any(arg != 0 for arg in found_arg)):
    logging.warning(" Please input all required arguments: \n" +
        " -s: Server IP Address \n" +
            " -p: Port Number \n" +
                " -u: Server Name \n" +
                    " -c: Password \n" +
                        " -r: Sensor value" )
    sys.exit()

# Create a UDP/IP socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info(" Socket created")
except socket.error, msg:
    logging.error("Could not create socket. Error Code : " + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

try:
    remote_ip = socket.gethostbyname(server)
except socket.gaierror, socket.herror: #need to validity of check IP address
    #could not resolve
    logging.error('Hostname ' + server + ' could not be resolved. Exiting')
    sys.exit()

server_address = (server, port)

waiting = True
i = 0
sock.settimeout(2)
gotSomething = False

#SENDING AUTH REQUEST
while (waiting and i < totalAttempts):
    try:
        logging.info(" Sending auth request")
        state = "0"
        try:
            sent = sock.sendto((state + "|" + authrequest), server_address)
            logging.info(" Sending attempt: " + str(i))
        except socket.error:
            logging.error("Did not pass in valid command line args")
            sys.exit()
        # Receive response
        randomstring, server = sock.recvfrom(4096)
        gotSomething = True
        logging.info(" Received challenge value from server")
        waiting = False

    except socket.timeout:
        i+=1
        logging.warning(" TIMED OUT in getting auth request, attempt: " + str(i))
        if i == totalAttempts:
            logging.error(" Too many timeouts --- assume server is down") #do we need to send a BYE message?
            sock.close()
            sys.exit()

    if gotSomething:
        try:
            state = "1"
            hashobject = hashlib.md5(username + password + randomstring).hexdigest()
            sent = sock.sendto((state + "|" + username + "," + str(hashobject) + "," + str(sensorvalue)), server_address)
            logging.info(" Sending the username: " + username +  " and the MD5 Hash: " + hashobject + " to the server")
            output = sock.recvfrom(4096)
            logging.info(" Successful Authentication. Received Sensor data from server")
            waiting = False
            print(output)
        except socket.timeout:
            i+=1
            logging.warning("TIMED OUT in getting back sensor data, attempt: " + str(i) + " out of 10")
            if i == totalAttempts:
                logging.error(" Too many timeouts --- assume server is down")
                sock.close()
                sys.exit()

#add a label at the fron of every message so server knows what it is!
#know when to send auth when to send other things

sys.exit()

#finally:
logging.info(" Closing socket")
sock.close()
