import bcrypt
import secrets


def encrypt_password(password:str) -> str: 
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        hashed_password = hashed.decode('utf-8')

        return hashed_password

def check_password(stored_hash:str, user_password:str)-> bool:    
    return bcrypt.checkpw(user_password.encode('utf-8'), stored_hash.encode('utf-8'))


def generate_api_key(length:int=32)-> str:

    return secrets.token_hex(length)
