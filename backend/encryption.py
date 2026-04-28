from cryptography.fernet import Fernet

# Generate key (only once in real apps)
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_file(data):
    return cipher.encrypt(data)

def decrypt_file(data):
    return cipher.decrypt(data)