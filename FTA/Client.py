import getopt
import sys
import threading
from mySocket import mySocket
import Queue
import logging

server = 'localhost'
port = 0
found_arg = [1]*2
window = 4

try:
   opts, args = getopt.getopt(sys.argv[1:],"A:P:",["address=","port="])
except getopt.GetoptError:
   print 'using default server [' + server + ']'

for opt, arg in opts:
    if opt in ("-A", "--address"):
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
    elif opt in ("-P", "--port"):
      if (arg.isdigit()):
        port = int(arg)
        found_arg[1] = 0
      else:
          logging.warning(" Port number must be a digit")
          sys.exit()
    else:
        print "Arguments are incorrect. Should be: " + sys.argv[0] + ' -A <address> -P <port>'
        sys.exit()

s = None

def connect():
    global s
    print('In connection')
    print('check')
    print("Server:", server)
    print("Port:", port)
    s = mySocket(server, port, False)
    logging.info("Socket created")

    synack = s.send_SYN()

def get(file):
    global s
    s.get_file(file)
    while True:
      status = s.listenforPacket()
      if status == "Done":
          if not (recv_data == "File not found\x1a"):
            f = open(s.filename, 'wb')
            f.write(s.recv_data)
            f.close()

def post(file):
    global s
    imageFile = open(file, "rb")
    s.post_file(imageFile, file)
    status = s.listenforPacket()
    if status == "Done":
      print s.recv_data


def window(size):
    print("window")

def invalid_input():
    print('--> Unknown command, please enter connect, get, post or window')

def main():
    cmd_actions = {'connect': connect, 'get': get, 'post': post, 'window': window}

    while 1:
        raw_input()   # After pressing Enter you'll be in "input mode"
        cmd = raw_input('Input command> ')

        if cmd == 'quit':
            break

        command_info = cmd.split(' ')
        method = command_info[0]
        if (len(command_info) > 1):
            para = command_info[1]

        action = cmd_actions.get(method, invalid_input)
        if (len(command_info) > 1):
            action(para)
        else:
            action()

main()
