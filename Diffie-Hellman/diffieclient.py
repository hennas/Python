import socket
import diffiesecret as d
import sys

secret = int(sys.argv[1]) #The secret key is given as a command line argument
port = 6567
host = 'localhost'

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

message = str(d.calculate_message(secret))
print("Sending: " + message)
socket.send(message.encode())

data = socket.recv(1024).decode()
print("Received: " + data)

revealedSecret = d.calculate_secret(data, secret)
print("The secret number: " + str(revealedSecret))

socket.close()