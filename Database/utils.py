import bcrypt
import secrets


def encrypt_password(password): 
        password = password.encode('utf-8')  # encode to bytes
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        hashed_password = hashed.decode('utf-8')

        return hashed_password

def check_password(stored_hash, user_password):    
    return bcrypt.checkpw(user_password.encode('utf-8'), stored_hash.encode('utf-8'))


def generate_api_key(length=32):

    return secrets.token_hex(length)
