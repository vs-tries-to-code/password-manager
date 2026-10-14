# Subrosa, a password manager
An open-source CLI tool to store your passwords (not perfectly, but quite) securely, built using Python.

# Libraries used
<ol>
<li>bcrypt - hash the master password</li>
<li>ryptography - encrypt and decrypt the stored password</li>
<li>scqlite3 - storage of password</li>
<li>hashlib - generate encryption key</li>
<li>base64 - encoding and decoding</li>
<li>os - urandom() to generate salt</li>
<li>questionary - to be questioned by the terminal</li> 
<li>rich - I love colours. For the user, it is for better visual signaling and look.</li>
</ol>