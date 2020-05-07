import socket
import sys
import curses
import os


def client_program():
    host = "127.0.0.1"
    port = int(sys.argv[1])  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(10).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection

#client_program()

def main(win,client_socket):
    win.nodelay(True)
    key=""
    while 1:          
        try:
           key = win.getkey()
           win.clear()
           if(key):
               #key caught, now send it to server and await reply
               client_socket.send(str(key).encode())  # send message
               data = client_socket.recv(10).decode()  # receive response
               win.addstr('Received from server: ')
               win.addstr(str(data))  # show in terminal
           key = win.getkey()
           win.clear()
           if key == os.linesep:
              break           
        except Exception as e:
           # No input   
           pass         

host = "127.0.0.1"
port = int(sys.argv[1])  # socket server port number
client_socket = socket.socket()  # instantiate
client_socket.connect((host, port))  # connect to the server

curses.wrapper(main,client_socket)

client_socket.close()
