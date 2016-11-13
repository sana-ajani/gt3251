import socket
import hashlib
import sys
import getopt
import logging
import os.path

server = "";
port = 0;
username = "";
password = "";
sensorvalue = "";
authrequest = "authrequest"
found_arg = [1] * 5

try:
   opts, args = getopt.getopt(sys.argv[1:],"s:p:u:c:r:d",["server=","port=","username=", "password=", "sensorvalue=", "debugging="])
except getopt.GetoptError:
   print 'using default server [' + str(server) + '] port [' + str(port) + ']'

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

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info(" Socket Created")
except socket.error:
    logging.error(" Failed to create socket")
    sys.exit()

try:
    remote_ip = socket.gethostbyname(server)
except socket.gaierror:
    logging.error(" Hostname could not be resolved. IP Address not correct format. Exiting")
    sys.exit()

try:
    s.connect((remote_ip, port))
    logging.info(" Socket connected to " + server + " on ip " + remote_ip)
except socket.error:
    logging.error(" Could not connect to a remote socket")
    sys.exit()

try :
    s.sendall(authrequest)
    logging.info(" Sending initial authentication request to server: " + str(server) + "on port: " + str(port))
except socket.error:
    #Send failed
    logging.error(" Auth request failed to send")
    sys.exit()

randomString = s.recv(4096)
logging.info(" Received challenge value from server")

hashobject = hashlib.md5(username + password + randomString).hexdigest()

try :
    s.sendall(username + "," + str(hashobject) + "," + str(sensorvalue))
    logging.info(" Sending the username: " + username +  " and the MD5 Hash: " + hashobject + "to the server")
except socket.error:
    logging.error(" Could not send username and hash to server")
    sys.exit()

output = s.recv(4096)
print output

s.close()

logging.info(" Socket closed")
