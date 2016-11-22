from Socket import Socket
import sys
import getopt


HOST = 'localhost'
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

socket = Socket(HOST, PORT, True)
socket.bind_server_socket()
while True:
    socket.receive_SYN()