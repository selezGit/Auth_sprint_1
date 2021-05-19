from dataclasses import dataclass

from Cryptodome.Cipher import PKCS1_OAEP, AES
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey.RSA import RsaKey
from Cryptodome.Random import get_random_bytes


@dataclass
class EncryptedMessage:
    nonce: bytes
    digest: bytes
    message: bytes


def generate_key_pair() -> (RsaKey, RsaKey):
    key = RSA.generate(2048)
    return key, key.publickey()


def encrypt_session_key(session_key: bytes, public_key: RsaKey) -> bytes:
    # Шифруем сессионный ключ с помощью публичного ключа
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    return enc_session_key


def decrypt_session_key(encrypted_session_key: bytes, private_key: RsaKey) -> bytes:
    # Расшифровываем сессионный ключ с помощью приватного ключа RSA
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(encrypted_session_key)

    return session_key


def encrypt(data: str, session_key: bytes) -> EncryptedMessage:
    # Шифруем и подписываем сообщение с помощью алгоритма симметричного блочного шифрования (AES).
    # Для таких алгоритмов используются режимы шифрования. В данном случае используется EAX режим,
    # который позволяет одновременно шифровать блоки данных и аутентифицировать их
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, digest = cipher_aes.encrypt_and_digest(data.encode())

    return EncryptedMessage(
        nonce=cipher_aes.nonce,
        digest=digest,
        message=ciphertext
    )


def decrypt(encrypted: EncryptedMessage, session_key: bytes) -> str:
    # Расшифровываем сообщение с помощью сессионного ключа по алгоритму AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, encrypted.nonce)
    data = cipher_aes.decrypt_and_verify(encrypted.message, encrypted.digest)

    return data.decode()


if __name__ == '__main__':
    raw = 'onlinecinema'
    session_key = get_random_bytes(16)
    priv_key, pub_key = generate_key_pair()

    # Сторона сервера
    encrypted_session_key = encrypt_session_key(session_key, pub_key)
    encrypted_data = encrypt(raw, session_key)
    print('Зашифрованный сессионный ключ:', encrypted_session_key)
    print('Зашифрованное сообщение:', encrypted_data.message)

    # Сторона клиента
    decrypted_session_key = decrypt_session_key(encrypted_session_key, priv_key)
    print('Расшифрованное сообщение:', decrypt(encrypted_data, decrypted_session_key))