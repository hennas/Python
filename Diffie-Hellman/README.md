A very simple demonstration of Diffie-Hellman key exchange. 

Diffiesecret.py - Stores the shared prime and shared base and performs calculations for the server and the client.

Diffieserver.py - Receives the public key from the client, shows the shared secret number and sends back its public key. Closes after a certain number of connections are made.

Diffieclient.py - Simply connects to the server, sends the public key, receives the public key of the server, 
                  shows the secret number and then closes the connection.
