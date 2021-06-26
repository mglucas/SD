from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# A enviará uma mensagem para B assinando (sign()) essa mensagem com sua chave
# privada e B verificará (verify()) a assinatura com a chave pública de A. 

# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/

# ---------

# Message
message = b'encrypt me!'

# A private key
# Loading
with open("private_key_a.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(), 
        password=None,
    )

# Signing
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

with open('msg_from_a.txt', 'wb') as f:
    f.write(signature)