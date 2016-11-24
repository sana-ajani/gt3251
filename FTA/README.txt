SANA AJANI & WILLIAM SU
PROGRAMMING SOCKET PROJECT 2


To run the server you will need to enter the following command:
python FTA-server.py <PORT NUMBER>

These are the list of commands one can do on the server:

window <WINDOW SIZE TO CHANGE TO> - changes the window size of server socket to specified

terminate - terminates server gracefully


To run the client you will need to enter the following command:
python FTA-client.py <SERVER IP ADDRESS> <SERVER PORT NUMBER>

These are the list of commands one can do on the client:

connect - connects the client socket to the server

window <WINDOW SIZE TO CHANGE TO> - changes the window size of client socket to specified

upload <file name> - uploads the file in the directory to the server

download <file name> - downloads the file in the server directory to the client

