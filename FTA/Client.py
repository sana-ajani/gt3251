import getopt
import sys
import threading
from mySocket import mySocket
import Queue
import logging

server = 'localhost'
PORT = 0
found_arg = [1]*2
window = 4
check = False

if len(sys.argv) < 3:
    print "Please enter the required parameters."
    sys.exit()
else:
    for arg in sys.argv[1:]:
        if ("." in arg):
            check = True
            server = arg
        elif (arg.isdigit()):
            PORT = int(arg)
        elif PORT == '':
            print "All arguments aren't present. Please enter in this form: " + sys.argv[0] + " <port>"
            sys.exit()
        elif not (check):
            logging.warning(" Please input a correct IP address")
            sys.exit()
        if arg == "-d":
            logging.basicConfig(level=logging.INFO)

s = None

def connect():
    global s
    logging.info(' Connecting...')
    s = mySocket(server, PORT, False)
    s.isConnected = True
    logging.info(" Initiating 3 way handshake. Sending SYN")
    synack = s.send_SYN()

#download
def get(file):
    global s
    s.get_file(file)
    while True:
        status = s.listenforPacket()
        if status == "Done":
            if not (s.recv_data == "File not found\x1a"):
                s.recv_data = s.recv_data.replace("\x1a", "")
                logging.info("This is the filename in the client: {0}".format(s.filename))
                f = open(s.filename, 'wb')
                f.write(s.recv_data)
                f.close()
                logging.info("Client has downloaded and created file")
                s.reset()
                return None
            else:
                logging.warning("File not found: ", s.filename)
                s.reset()
                return None

#upload
def post(file):
    global s
    try:
        imageFile = open(file, "rb")
        s.post_file(imageFile, file)
    except IOError:
        logging.warning("File to upload is not found: ", file)
        return None
    while True:
      status = s.listenforPacket()
      if status == "Done":
        logging.info(" Data received. {0}".format(s.recv_data))
        s.reset()
        return None


def window(size):

    s.change_window(int(size))
    logging.info(" Window changed")

def invalid_input():
    logging.warning('--> Unknown command, please enter connect, get <download filename>, post <upload filename> or window <desired window size>')

def main():
    global s
    cmd_actions = {'connect': connect, 'get': get, 'post': post, 'window': window}

    while 1:
        raw_input("Press enter to enter new command")   # After pressing Enter you'll be in "input mode"
        cmd = raw_input('Input command> ')

        if cmd == 'disconnect':
            logging.info("Initiating disconnect. Sent FIN packet")
            s.send_FIN()
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
