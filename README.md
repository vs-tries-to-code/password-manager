# Password Manager
An open-source CLI tool to store your passwords (not perfectly, but quite) securely, built using Python. 

# Libraries used
bcrypt - hash the master password
cryptography - encrypt and decrypt the stored password
sqlite3 - storage of password
hashlib - generate encryption key
base64 - encoding and decoding
getpass - input password in secret (the Linux way)
os - urandom() to generate salt