# This program uses FERNET to hash/encrypt passwords
#
# tsvetelin.maslarski-ext@ldc.com

from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"k: {key.decode()}")

key = 'WC3Q8ZvuCQd1s6wIxvfKEtMz9S0zbRU8fxDPGNBUxsg='
cip = Fernet(key)
password = 'some_password'
enc_p = cip.encrypt(b"password")
print(f"p: {enc_p.decode()}")
