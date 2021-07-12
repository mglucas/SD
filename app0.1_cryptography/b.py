from inspect import signature
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

# A enviará uma mensagem para B assinando (sign()) essa mensagem com sua chave
# privada e B verificará (verify()) a assinatura com a chave pública de A. 

# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/

# ---------

# Message
message = b'encrypt me!'

# A - public key
# Loading
with open("public_key_a.pem", "rb") as key_file:
    public_key  = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()        
    )

# Loading message
with open("msg_from_a.txt", "rb") as f:
    signature  = f.read()

# Verify

try:
    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Valid signature")
except InvalidSignature :
    print("Invalid signature")

