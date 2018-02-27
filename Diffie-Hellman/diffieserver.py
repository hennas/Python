import socket
import diffiesecret as d
from threading import Thread

secret = 3
port = 6567
connections = []
numOfConnections = 2 #How many connections are allowed before closing the socket

def clientthread(conn):
        while True:
                data = conn.recv(1024).decode()
                if not data:
                        break
                print("Received: " + data)
                
                revealedSecret = d.calculate_secret(data, secret)
                print("The secret number: " + str(revealedSecret))
                
                reply = str(d.calculate_message(secret))
                print("Sending back: " + reply)
                
                conn.sendall(reply.encode())      
        conn.close()
        
        
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', port))
serversocket.listen(5)
while True:
        conn, addr = serversocket.accept()
        connections.append(conn)
        Thread(target = clientthread, args=(conn,)).start()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        if len(connections) == numOfConnections:
            break;
        
serversocket.close()
