import requests
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

API_URL = "https://api.bhasika.com/testnp/blogs/get-blog-pageable"
row = 10
page = 1

# --- AES-GCM parameters ---
KEY_SIZE = 32  # 256 bits
IV_SIZE = 12  # 12 bytes
TAG_SIZE = 16  # 128 bits (cryptography handles this internally)


def generate_key():
    return os.urandom(KEY_SIZE)


def encrypt(plain_text, key):
    iv = os.urandom(IV_SIZE)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(iv, plain_text.encode(), None)
    cipher_with_iv = iv + ct
    return base64.b64encode(cipher_with_iv).decode()


def decrypt(cipher_text_b64, key):
    cipher_with_iv = base64.b64decode(cipher_text_b64)
    iv = cipher_with_iv[:IV_SIZE]
    ct = cipher_with_iv[IV_SIZE:]
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(iv, ct, None)
    return pt.decode()


# --- Prepare key and token ---
key = generate_key()
key_b64 = base64.b64encode(key).decode()

token_payload = {
    "t": int(os.times()[4] * 1000),
    "url": "https://api.bhasika.com/testnp/blogs/get-blog-pageable",
}
token_json = json.dumps(token_payload)
token_encrypted = encrypt(token_json, key)

headers = {
    "key": key_b64,
    "token": token_encrypted,
}


while True:
    payload = {"row": row, "page": page}
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch blogs: {response.status_code}")
        print("Error message:", response.text)
        break

    blogs = response.json()
    content = blogs.get("data", {}).get("content", [])
    if not content:
        break

    for blog in content:
        print(page, blog)

    total_pages = blogs.get("data", {}).get("totalPages", 1)
    if page >= total_pages:
        break
    page += 1
