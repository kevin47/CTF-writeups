# Lazy House
* There is an integer overflow when checking for money, therefore we could buy a house of huge size `x` such that `x*218 mod (2**64) is smaller than 116630` and bypass it. In this case I used `2792397038680803685`. Selling the house will basically give us unlimited money.
* Thanks to Samuel for finding the number for me.
* After that we can allocate some chunks and use `Upgrade` to overflow the size to a bigger size. Thus leaking `libc addres` and `heap address`.
* Since now we have overlapped chunks. We can easily perform `largebin corruption attack (from House of Storm)`, which give us the ability to overwrite two arbitrary addresses' value into a heap address.
* We just need one in this case, which is `tcache_perthread_struct *tcache` in `libc`. This is a pointer in libc which indicates where the `tcache_perthread_struct` is (usually in the beginning of the heap).
* We successfully hijacked`tcache_perthread_struct` to our controllable chunk. We need this because `calloc` doesn't allocate chunks from tcache and the only `malloc` we have is from `Buy a super house` which can only be used once. This will prevent tcache poisoning from working since we need multiple mallocs.
* Fake `tcache_perthread_struct` such that mallocing chunk 0x217 will be on `__malloc_hook`.
* Overwrite `__malloc_hook` into
    ```
    libc_base + 0xd8db1:
        lea rsp,[rbp-0x28]
        pop rbx
        pop r12
        pop r13
        pop r14
        pop r15
        pop rbp
        ret
    ```
* Through observation, in this binary, when callocing, `rbp` happens to be the desired size. Therefore we can control the `rsp` through callocing a size equal to heap address. And perform ROP since then.
* I suppose that this is an unintended solution since I only used `Upgrade` once instead of twice.
