CS3251-A Sockets Programming Assignment 2

Project Description: Client-Server File Transfer app using our CRP protocol

Submitted: 11/24/2016

Sana Ajani - sajani6@gatech.edu
Will Su - wwilliam6@gatech.edu


To run our program, open up two docker containers. 

To run the server: python Server.py <port num> -d
To run the client: python Client.py <server IP> <port num> -d

Client commands:
connect
    -The FTA-client connects to the FTA-server. 
get F
    -The FTA-client downloads file F from the server (if F exists in the same directory with the FTA-server program). 
post F
    -The FTA-client uploads file F to the server (if F exists in the same directory with the FTA-client program).

window W
    -W: the maximum receiver’s window-size at the FTA-Client (in segments). 

disconnect
    -The FTA-client terminates gracefully from the FTA-server. 

Server commands:
window W
    -W: the maximum receiver’s window-size at the FTA-Server (in segments). 
terminate
    -Shut-down FTA-Server gracefully.

Attached files:

Client.py - our FTA-Client to initiate file transfer
Server.py - our FTA-Server to listen/respond to Client requests
mySocket.py - our Socket class with all methods to send and receive
Packet.py - our Packet class contains the header and data

Sample.pdf - attached sample output
UpdatedAPI.pdf - updated API of our initial CRP protocol design
 
README.md
