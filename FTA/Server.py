from mySocket import mySocket
import sys
import getopt


HOST = '172.17.0.2'
PORT = ''

try:
   opts, args = getopt.getopt(sys.argv[1:],"X:",["port="])
except getopt.GetoptError:
    print "Enter valid parameters."
    sys.exit()

for opt, arg in opts:
    if opt in ("-X", "--port"):
        PORT = int(arg)
    else:
        print "Arguments are incorrect. Should be: " + sys.argv[0] + ' -X <port>'
        sys.exit()

if (PORT == ''):
    print "All arguments aren't present. Please enter in this form: " + sys.argv[0] + " -X <port>"
    sys.exit()

socket = mySocket(HOST, PORT, True)
socket.bind_server_socket()
while True:
    socket.receive_SYN()
