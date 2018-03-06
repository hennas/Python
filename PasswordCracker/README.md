The file 'md5hashed' contains usernames and their corresponding MD5 hashed passwords in the format 'username:MD5hashedPassword'.

Pwdcracker.py gets the forementioned file as a command line argument and then starts a loop, where it generates a random password, hashes it 
and checks if there's a match in the file for the random password. If it finds a match, it saves the username and the decrypted password 
into a file.
