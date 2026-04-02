from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import pbkdf2_hmac
import numpy as np
import argparse
import os
import hashlib
import random



def pixel_order(arr_len, password):
    seed = int.from_bytes(hashlib.sha256(password.encode()).digest(), 'big')
    rng = random.Random(seed)
    indices = list(range(arr_len))
    rng.shuffle(indices)
    return indices


def bytes_to_bits(data: bytes):
    return [int(b) for byte in data for b in f"{byte:08b}"]


def bits_to_bytes(bits):
    return bytes(int("".join(str(b) for b in bits[i:i+8]), 2)
                 for i in range(0, len(bits), 8))


'''
Header structure with byte length:
[length][salt][nonce][tag]
   4      16    16    16
'''
def add_header(salt: bytes, nonce: bytes, payload: bytes, tag: bytes):
    preambel = len(payload)
    return preambel.to_bytes(4, 'big') + salt + nonce + tag + payload


def openImage(path):
    im = Image.open(path)
    imArr = np.array(im, dtype=np.uint8)
    im.close()
    return imArr


def binFromChar(c):
    x = [int(x) for x in bin(ord(c))[2:]]
    x = [0]*(8-len(x)) + x
    return x


def binFromStr(s):
    res = []
    for c in s:
        res += binFromChar(c)
    res += [0]*8
    res = np.array(res, dtype=np.uint8)
    return res



def encrypt(payload: bytes, password: str):
    salt = get_random_bytes(16)
    key = pbkdf2_hmac("sha256", password.encode(), salt, 200000, dklen=32)

    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(payload)

    return salt, cipher.nonce, ciphertext, tag


def decrypt(salt, nonce, ciphertext, tag, password):
    key = pbkdf2_hmac("sha256", password.encode(), salt, 200000, dklen=32)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)



def encode(image, payload, pwd, outPath='encoded.png'):
    imageArr = openImage(image)
    imgRnd = imageArr - imageArr%2
    imgFlat = imgRnd.flatten()

    salt, nonce, secret, tag = encrypt(payload, pwd)
    secret = add_header(salt, nonce, secret, tag)
    bits = bytes_to_bits(secret)

    if len(bits) > len(imgFlat):
        raise ValueError("Message too large for image")


    order = pixel_order(len(imgFlat), pwd)

    for bit, idx in zip(bits, order):
        imgFlat[idx] = (imgFlat[idx] & 0xFE) | bit



    imgRnd = np.reshape(imgFlat, np.shape(imageArr))
    img = Image.fromarray(imgRnd)
    img.save(outPath)


def decode(image, pwd):
    imgArr = openImage(image)
    imgFlat = imgArr.flatten()
    order = pixel_order(len(imgFlat), pwd)

    header_length = 52 * 8 # 48 bytes
    header_bits = [imgFlat[i] % 2 for i in order[:header_length]]
    header = bits_to_bytes(header_bits)

    length = int.from_bytes(header[0:4], 'big') #4 bytes
    salt = header[4:20] #16 bytes
    nonce = header[20:36] #16 bytes
    tag = header[36:52] #16 bytes

    payload_bits = length * 8
    payload = [imgFlat[i] % 2 for i in order[header_length:header_length + payload_bits]]

    payload = bits_to_bytes(payload)
    msg = decrypt(salt, nonce, payload, tag, pwd)

    return msg



if __name__ == '__main__':
    parser = argparse.ArgumentParser('Steganography')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-e', '--encode', action='store_true', help='Encode data into image')
    mode.add_argument('-d', '--decode', action='store_true', help='Decode data from image')

    parser.add_argument('-m', '--message', help='Message to encode (text mode)')
    parser.add_argument('-f', '--file', help='Path to file to embed')
    parser.add_argument('-o', '--output', help='Output file (for encoded image or extracted payload)')
    parser.add_argument('-i', '--image', required=True, help='Path to image')
    parser.add_argument('-p', '--password', required=True, help='Password for embedding/extraction')

    args = parser.parse_args()


    if args.encode:
        if args.message:
            payload = args.message.encode("utf-8")
        elif args.file:
            with open(args.file, "rb") as f:
                payload = f.read()
        else:
            raise ValueError("You must provide either --message or --file for encoding")

        encode(args.image, payload, args.password, args.output)

    elif args.decode:
        payload = decode(args.image, args.password)

        if args.output:
            with open(args.output, "wb") as f:
                f.write(payload)
        else:
            try:
                print(payload.decode("utf-8"))
            except UnicodeDecodeError:
                print("Decoded binary data (use --output to save it)")


