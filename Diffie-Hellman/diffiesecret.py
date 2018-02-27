#A module that stores the shared prime and base. 
#This is used by both the server and the client to calculate the shared secret number (calculate_secret) and the public key (calculate_message) that is send through the connection
sharedprime = 23
sharedbase = 5

def calculate_message(secret):
        return (sharedbase ** secret) % sharedprime

def calculate_secret(received, secret):
        return (int(received) ** secret) % sharedprime
