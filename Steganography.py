from PIL import Image
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import pbkdf2_hmac
import numpy as np
import argparse
import os
import hashlib
import random


ROOT = os.path.dirname(os.path.realpath(__file__))


class Steganography():
    def __init__(self, mode, out, pwd, img, txt=None):
        self.__mode = mode #0: Encode | 1: Decode
        self.__out = out
        self.__pwd = pwd
        self.__img = img
        self.__txt = txt

    @property
    def mode(self):
        return self.__mode
    
    @mode.setter
    def mode(self, mode):
        self.__mode = mode

    @property
    def out(self):
        return self.__out
    
    @out.setter
    def out(self, out):
        self.__out = out

    @property
    def pwd(self):
        return self.__pwd
    
    @pwd.setter
    def pwd(self, pwd):
        self.__pwd = pwd

    @property
    def img(self):
        return self.__img
    
    @img.setter
    def img(self, img):
        self.__img = img

    @property
    def txt(self):
        return self.__txt
    
    @txt.setter
    def txt(self, txt):
        self.__txt = txt

         
    def __pixel_order(self, arr_len, password):
        seed = int.from_bytes(hashlib.sha256(password.encode()).digest(), 'big')
        rng = random.Random(seed)
        indices = list(range(arr_len))
        rng.shuffle(indices)
        return indices


    def __bytes_to_bits(self, data: bytes):
        return [int(b) for byte in data for b in f"{byte:08b}"]


    def __bits_to_bytes(self, bits):
        return bytes(int("".join(str(b) for b in bits[i:i+8]), 2)
                    for i in range(0, len(bits), 8))


    '''
    Header structure with byte length:
    [length][salt][nonce][tag]
    4      16    16    16
    '''
    def __add_header(self, salt: bytes, nonce: bytes, payload: bytes, tag: bytes):
        preambel = len(payload)
        return preambel.to_bytes(4, 'big') + salt + nonce + tag + payload


    def __openImage(self, path):
        im = Image.open(path)
        imArr = np.array(im, dtype=np.uint8)
        im.close()
        return imArr


    def __binFromChar(self, c):
        x = [int(x) for x in bin(ord(c))[2:]]
        x = [0]*(8-len(x)) + x
        return x


    def __binFromStr(self, s):
        res = []
        for c in s:
            res += self.__binFromChar(c)
        res += [0]*8
        res = np.array(res, dtype=np.uint8)
        return res


    def __encrypt(self, payload: bytes, password: str):
        salt = get_random_bytes(16)
        key = pbkdf2_hmac("sha256", password.encode(), salt, 200000, dklen=32)

        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(payload)

        return salt, cipher.nonce, ciphertext, tag


    def __decrypt(self, salt, nonce, ciphertext, tag, password):
        key = pbkdf2_hmac("sha256", password.encode(), salt, 200000, dklen=32)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)


    def __encode(self, image, payload, pwd, outPath='encoded.png'):
        imageArr = self.__openImage(image)
        imgRnd = imageArr - imageArr%2
        imgFlat = imgRnd.flatten()

        salt, nonce, secret, tag = self.__encrypt(payload, pwd)
        secret = self.__add_header(salt, nonce, secret, tag)
        bits = self.__bytes_to_bits(secret)

        if len(bits) > len(imgFlat):
            raise ValueError("Message too large for image")


        order = self.__pixel_order(len(imgFlat), pwd)

        for bit, idx in zip(bits, order):
            imgFlat[idx] = (imgFlat[idx] & 0xFE) | bit


        imgRnd = np.reshape(imgFlat, np.shape(imageArr))
        img = Image.fromarray(imgRnd)
        img.save(outPath)


    def __decode(self, image, pwd):
        imgArr = self.__openImage(image)
        imgFlat = imgArr.flatten()
        order = self.__pixel_order(len(imgFlat), pwd)

        header_length = 52 * 8 # 48 bytes
        header_bits = [imgFlat[i] % 2 for i in order[:header_length]]
        header = self.__bits_to_bytes(header_bits)

        length = int.from_bytes(header[0:4], 'big') #4 bytes
        salt = header[4:20] #16 bytes
        nonce = header[20:36] #16 bytes
        tag = header[36:52] #16 bytes

        payload_bits = length * 8
        payload = [imgFlat[i] % 2 for i in order[header_length:header_length + payload_bits]]

        payload = self.__bits_to_bytes(payload)
        msg = self.__decrypt(salt, nonce, payload, tag, pwd)

        return msg

    
    def run(self):
        if not self.mode: #Encode
            with open(self.txt, "rb") as f:
                payload = f.read()
                f.close()

            self.__encode(self.img, payload, self.pwd, ROOT + '/out/' + self.out)

        elif self.mode: #Decode
            payload = self.__decode(self.img, self.pwd)
            if self.out:
                with open(ROOT + '/out/' + self.out, "wb") as f:
                    f.write(payload)
                    f.close()
            else:
                try:
                    print(payload.decode("utf-8"))
                except UnicodeDecodeError:
                    print("Decoded binary data (use --output to save it)")



if __name__ == '__main__':

    parser = argparse.ArgumentParser('Steganography')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-e', '--encode', action='store_true', help='Encode data into image')
    mode.add_argument('-d', '--decode', action='store_true', help='Decode data from image')

    parser.add_argument('-t', '--text', help='Path to file to embed')
    parser.add_argument('-o', '--output', help='Output file (for encoded image or extracted payload)')
    parser.add_argument('-i', '--image', required=True, help='Path to image')
    parser.add_argument('-p', '--password', required=True, help='Password for embedding/extraction')

    args = parser.parse_args()

    if args.encode:
        mode = 1
    elif args.decode:
        mode = 0
    
    stego = Steganography(mode, args.output, args.password, args.image, args.text)
    stego.run()

