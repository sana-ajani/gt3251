from mySocket import mySocket
import sys
import getopt
import threading
import logging

HOST = '172.17.0.2'
PORT = ''

#arguments in the form python Server.py <port name> -d
if len(sys.argv) < 2:
    print "Please enter the required parameters."
    sys.exit()
else:
    for arg in sys.argv[1:]:
        if (arg.isdigit()):
            PORT = int(arg)
        elif PORT == '':
            print "All arguments aren't present. Please enter in this form: " + sys.argv[0] + " <port>"
            sys.exit()
        if arg == "-d":
            logging.basicConfig(level=logging.INFO)

socket = mySocket(HOST, PORT, True)
socket.bind_server_socket()

# 3 way handshake
def listen():
    logging.info(" Socket waiting for a connection")
    socket.wait_for_connect()
    socket.isConnected = True
    while True:
        status = socket.listenforPacket()
        if status == "Done":
            #print "Done"
            if socket.isDownload:
                #download the file
                split = str(socket.recv_data).split('dnld')
                name_with_end = split[1]
                split = name_with_end.split('\x1a')
                socket.filename = split[0]
                filename = socket.filename
                logging.info(" Received file from client")

                try:
                    f = open(filename, 'rb')
                    content_string = f.read()
                    f.close()
                    b = bytearray(content_string)
                    b.append(26)
                    socket.reset()
                    socket.send(b)
                    socket.recv_data = bytearray()
                    logging.info(" Sent the requested file: {0} back to the client.".format(filename))

                except IOError:
                    logging.warning(" Could not find requested file in directory")
                    toSend = "File not found"
                    b = bytearray(toSend)
                    b.append(26)
                    socket.send(b)

                socket.reset()

            else:
                #upload the file
                split = str(socket.recv_data).split("upld")
                #split filename with file content
                filename_content_begin_end = split[1]
                split = filename_content_begin_end.split(chr(2))
                filename_content_end = split[1]
                split = filename_content_end.split(chr(3))
                content = split[1]
                filename = split[0]
                socket.filename = filename
                content = content.replace('\x1a', '')

                try:
                    f = open(filename, 'wb')
                    f.write(content)
                    f.close()
                except IOError:
                    logging.warning(" Could not upload file to server")
                socket.recv_data = bytearray()

                done_upload = "Upload finished"
                b = bytearray(done_upload)
                b.append(26)
                socket.reset()
                socket.send(b)
                logging.info(" Received and uploaded file to server: {0}".format(filename))
                socket.reset()


def window(size):
    socket.change_window(int(size))
    logging.info(" Window changed")

def invalid_input():
    logging.warning('--> Unknown command, please enter window <desired window size> or terminate')

def main():
    cmd_actions = {'window': window}
    thread = threading.Thread(target = listen)
    thread.daemon = True
    thread.start()
    while 1:
        raw_input("Press enter to enter new command \n")
        cmd = raw_input('Input command> ')
        if cmd == 'terminate':
            #gracefully terminate the connection
            if (socket.isConnected):
                logging.info(" Sent FIN packet to complete termination")
                socket.send_FIN()
            else:
                logging.info(" Shutting down server")
                socket.socket.close()
            break

        command_info = cmd.split(' ')
        method = command_info[0]
        if (len(command_info) > 1):
            para = command_info[1]

        action = cmd_actions.get(method, invalid_input)
        if (len(command_info) > 1):
            action(para)
        else:
            if (method == "window"):
                logging.warning(" Please input a window size")
                return None
            action()

main()
