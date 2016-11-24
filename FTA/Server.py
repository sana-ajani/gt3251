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
        print "Done"
        if socket.isDownload:
            #download the file
            split = str(socket.recv_data).split('dnld')
            print split
            name_with_end = split[1]
            split = name_with_end.split('\x1a')
            socket.filename = split[0]

            filename = socket.filename
            print "THIS IS THE FILENAME!!", filename
            print "LENGTH OF IT!", len(filename)

            try:

                f = open(filename, 'rb')
                content_string = f.read()
                f.close()
                b = bytearray(content_string)
                b.append(26)
                socket.send(b)
                socket.recv_data = bytearray()
                print "Server sent the file back to the client:", filename

            except IOError:
                print 

                toSend = "File not found"

                b = bytearray(toSend)
                b.append(26)
                socket.send(b)

        else:
            #upload the file
            split = str(socket.recv_data).split("upld")

            filename_content_begin_end = split[1]

            split = filename_content_begin_end.split(chr(2))

            filename_content_end = split[1]

            split = filename_content_end.split(chr(3))

            content = split[1]

            filename = split[0]



            socket.filename = filename
            print "THIS IS THE FILENAME!!", filename
            print "LENGTH OF IT!", len(filename)
            try:
                f = open(filename, 'wb')
                f.write(content)
                f.close()
            except:
                print "ERRORRR"
            socket.recv_data = bytearray()

            done_upload = "Done upload"
            b = bytearray(done_upload)
            b.append(26)
            socket.send(b)
            print "Server received and uploaded file:", filename
