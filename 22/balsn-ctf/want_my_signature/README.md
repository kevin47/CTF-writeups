## Want my signature?

- The service accepts a signed tar file, the file authenticity is protected by a hash list having the files' hashes, and a signature signing the hash list. The chain of protection `signature => hash list => files` enforces that any changes made on the files or hash list is invalid
- The verification process basically traverses the hash list and checks whether the file's hash is correct. But in the opposite direction when checking if all the files' hash are correct in the hash list, it only checks for regular files since the hash of symlink, dev, etc. are ambiguous
- Here we discover the first logic bug: a symlink can be added into the tar without being detected
- The second bug comes from the process of checking path traversal. `realpath` resolves a filename to the destination buffer, which is of size 512. However, the maximun length of a filename can be 4096, which causes buffer overflow
- The binary is compiled without PIE and canary, by combining the two vulnerabilities above, we get to ROP easily
- The ROP length will be very limitted at first since it'll easily overwrite base dir, causing the realpath comparison to fail. The solution we used is to put the symlinks deep in the dirs so that `traverse_dir()` is called recursively, thus lengthening the range between path name and base dir
- The ROP is very similar to the challenge De-ASLR on [pwnable.tw](https://pwnable.tw), with 2 limitations:
    - We can only input once
    - We can't leak address
- Knowing that, our goal become calling `system(reverse_shell_cmd)`
- There are two key ROP gadgets here:
    - `add dword ptr [rbp + X], ebx`
        - This allow us to write ROP and reverse_shell_cmd on the bss
    - `__libc_csu_init`
        - Calling this function has no effect, but it push `r13, r14` into stack (which we migrate to bss later)
- Therefore, our ROP process becomes:
    - Use `add dword ptr [rbp + X], ebx` to write ROP2 right next to the GOT segment and reverse_shell_cmd into bss
    - Use `pop rsp; pop r13; pop r14; pop r15; ret` to set `rsp` into the tail of GOT, some libc address will then be popped into `r13, r14`
    - We now stack migrated to bss. Use `__libc_csu_init` to push `r13, r14`, which contains libc address into the bss
    - Last, use `add dword ptr [rbp + X], ebx` to add the libc address in the bss to `system` and return to it. Enjoy the reverse shell ;)
- BTW, the vmdk was there because we need to know the order of `readdir` in order to build ROP with filenames. And we found out the order is actually dependent to kernel the day before the competition. So the vmdk was added to get the correct order. I am sorry if someone was misled and thought the private key of the signature could be found in it

