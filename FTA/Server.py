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

# 3 way handshake
socket.wait_for_connect()

while True:
    status = socket.listenforPacket()
    if status == "Done":
        if socket.isDownload:
            #download the file
            filename = socket.filename
            try:

                f = open(filename, 'rb')
                content_string = f.read()
                f.close()
                b = bytearray(content_string)
                socket.send(b)
                socket.recv_data = bytearray()

            except IOError:

                toSend = "File not found"

                b = bytearray(toSend)
                b.append(26)
                socket.send(b)

            print "Server sent the file back to the client:", filename



        else:
            #upload the file
            filename = socket.filename
            content = socket.recv_data
            f = open(filename, 'wb')
            f.write(content)
            f.close()
            socket.recv_data = bytearray()

            done_upload = "Done upload"
            b = bytearray(done_upload)
            b.append(26)
            socket.send(b)
            print "Server received and uploaded file:", filename




