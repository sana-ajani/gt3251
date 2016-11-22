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



def console(q, lock):
    while 1:
        raw_input()   # After pressing Enter you'll be in "input mode"
        with lock:
            cmd = raw_input('Input command> ')

        q.put(cmd)
        if cmd == 'quit':
            break

def connect(lock):
    with lock:
        print('In connect')
        s = mySocket(server, port, False)
        logging.info("Socket created")

        synack = s.send_SYN()
        if (synack):
            s.send_ACK(synack.ack_num, synack.seq_num + 1)

def get(file, lock):
    with lock:
        print('--> action bar')

def post(file, lock):
    with lock:
        print("post")

def window(size, lock):
    with lock:
        print("window")

def invalid_input(lock):
    with lock:
        print('--> Unknown command, please enter connect, get, post or window')

def main():
    cmd_actions = {'connect': connect, 'get': get, 'post': post, 'window': window}
    cmd_queue = Queue.Queue()
    stdout_lock = threading.Lock()

    dj = threading.Thread(target=console, args=(cmd_queue, stdout_lock))
    dj.start()

    while 1:
        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        command_info = cmd.split(' ')
        method = command_info[0]
        if (len(command_info) > 1):
            para = command_info[1]

        action = cmd_actions.get(method, invalid_input)
        if (len(command_info) > 1):
            action(para, stdout_lock)
        else:
            action(stdout_lock)

main()
