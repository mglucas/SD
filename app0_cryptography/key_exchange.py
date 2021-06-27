from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/

def main():
        
    # Priv pub key - A 
    private_key_a = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key_a = private_key_a.public_key()
    
    # Priv pub key - B
    private_key_b = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key_b = private_key_b.public_key()

    # Storing private keys
    # A
    pem_priv_a = private_key_a.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('private_key_a.pem', 'wb') as f:
        f.write(pem_priv_a)

    # B
    pem_priv_b = private_key_b.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('private_key_b.pem', 'wb') as f:
        f.write(pem_priv_b)

    # Storing public keys
    # A
    pem_pub_a = public_key_a.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('public_key_a.pem', 'wb') as f:
        f.write(pem_pub_a)

    # B
    pem_pub_b = public_key_b.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('public_key_b.pem', 'wb') as f:
        f.write(pem_pub_b)


if __name__ =='__main__':
    main()