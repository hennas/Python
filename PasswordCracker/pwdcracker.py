import sys
import subprocess
import random
import string

characters = string.ascii_letters + string.digits + string.punctuation
used = []

def generate_password():
    """Generates random passwords"""
    password = ""
    wordlength = random.randint(4, 6)
    while True:
        for i in range(wordlength):
            randomcharacter = random.randint(0, len(characters) - 1)
            password += characters[randomcharacter]
        if password in used:
            continue
        else:
            used.append(password)
            return password
            
def splitdata(data):
    """Replaces each string line in data with a list that consists of two parts: the username and the corresponding hashed password"""
    for i, line in enumerate(data):
        data[i] = line.split(":")

def match(hash, data):
    """Goes through the data and when it finds the hash that matches with the hash of our generated password, it returns the username"""
    for line in data:
        if line[1] == hash:
            return line[0]
            
def execute(file):
    """
    Does the password cracking: After handling the data the function starts a loop that generates a random password, hashes it with md5 
    and then compares the hash with the hashes in the data. If a match is found, the function match() is called to combine the found password with the right username.
    Finally writefile() is called in order to save the username and the decrypted password.
    """
    data = readfile(file)
    splitdata(data)
    while True:
        password = generate_password()
        p1 = subprocess.Popen(["echo", "-n", password], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["md5sum"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = subprocess.Popen(["cut", "-d", " ", "-f1"], stdin=p2.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        p2.stdout.close()
        output, err = p3.communicate() # Output is the MD5 hash of the generated password
        for user, hash in data: 
            if output == hash: #Checks if there's a match between the hash of the generated password and the hash of a password in the data
                user = match(hash, data)
                writefile("solved.txt", user, password)
                
def readfile(file):
    """
    Reads the data from the file. The data is in the following format:   
    username:MD5hashedPassword
    """
    try:
        with open(file) as source:
            data = source.readlines()
            return data 
    except IOError:
        print("Error while reading the file")

def writefile(file, user, password):
    """
    If the hashed version of the generated password matches with a hashed password in the file, this function is called and 
    the decrypted password with the corresponding username is written to the file named solved.txt
    """
    try:
        with open(file, 'a') as target:
            target.write(user + ' ' + password + '\n')
    except IOError:
        print("Error while writing to the file")

passwordfile = sys.argv[1] #The file containing usernames and the corresponding hashed passwords is given as a command line argument. 
execute(passwordfile)
