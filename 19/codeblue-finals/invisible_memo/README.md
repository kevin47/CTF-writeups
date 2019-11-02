# CODE BLUE CTF 2019 Finals

## InvisibleMemo
* This is probably one of the most interesting challenge I've solved recently.

### TL;DR

* Vulnerability: Delete index is uninitialized.
* Free chunk in the key with delete -1.
* Send the chunk into smallbin.
* Bypass calloc zeroing by setting the 0x2 bit.
* Leak the upper part of libc using delete -5.
* Leak the lower part of libc using add to leak it byte by byte.
* Modify unsorted bin's size.
* Allocate a huge chunk on stack from unsorted bin.
* ROP.

### TS;WM

* The binary is pretty simple. At the beginning we can choose the size of the key. It's buffer is mmaped when its size is larger than 0x40; otherwise it is on the stack. Nonetheless, I found this useless, just leave it on the stack.
* You have three actions `Add`, `Delete`, and `Change Key`.
* `Add` requires us to enter the right key, and then allocates the size we want using `calloc` if size <= 0x408, `malloc` otherwise. It immediately comes into my mind that this could be use to leak as a side channel attack since we can't show the memos.
* We only have 3 slots for the memos.
* Note that we could only allocate 5 times in total. There is a iterator that increases every time we successfully allocate a memo, the program uses it as the memo id. However, **if we enter `offset` greater than `size`, the allocated buffer is freed and the iterator wouldn't be increased**. This is super important!
* Given a memo's id, `Delete` find the corresponding id in the 3 slots, and frees it.
* `Change Key` just let us re-enter the key.
* The vulnerability is tricky to find. I thought it was a double free at first because `Delete` doesn't clear out the pointer after freeing. But I immediately realized that there was a bit marking if the slot is inuse or not.
* After some analyzing, I found something interesting:
```
stack:
    0x7ffca26c1480: 0x0000000100000001      0x00007f5752a12005
    0x7ffca26c1490: 0x0000000100000001      0x0000561e9bc85260
    0x7ffca26c14a0: 0x0000000200000001      0x0000561e9bc85280
    0x7ffca26c14b0: 0x0000000300000001      0x0000561e9bc852a0
```
* The bottom 3 lines are the 3 slots for memo, the fields are `id`, `inuse bit`, and `pointer to memo`. The first line, however, are some values left on the stack and looks pretty similar the structure of memos. The address actually is inside of the key. So... what if we could `Delete(-1)`?
* From static analysis, we could see the index that `Delete` uses is actually not initialized. However, when dynamic analyzing, it starts from 0 every time.
* After some further investigation, I found that when selecting `Delete`, instead of simply sending "2", we could send `"2"+"\x00"*10+p8(-1)`, that will let `Delete` start searching from index -1. Boom!! (The reason why it always starts with 0 before is because `getint()` actually clears out the buffer)
* This gives us a primitive of freeing a chunk of memory on stack. Because the content of the key could be changed whenever we want, we could fake a valid chunk in it. Note  that this could only be freed once, since the `inuse` bit couldn't be set back to 0x1 once it is zeroed.
* Now that we can free a chunk in the key. There could be either a libc address or a heap address in the key. Either way, we should find a way to leak it, since we can't print the key directly.
* The first thought that comes in mind is to partial overwrite the key byte by byte with `Change key`. Then we guess all the 256 possibilities for a byte with `Add` because it tell us if we entered a right key or not.
* Keep in mind that once we guessed a byte, the rest of the address desired to leak is destroyed by partial overwriting. Therefore, we need a way to restore the address.
* The way to restore may differ depending on which address we choose to. Here we choose libc address directly since we'll need it anyway when hijacking control flow. Also, only calling `Add` 5 times successfully limits us to leak both libc and heap address. 
* The way we leave libc address in the key is by:
```
stack:
    key+0x00: 0x0000000000000000      0x0000000000000021
    key+0x10: 0x0000000000000000      0x0000000000000000 
    key+0x20: 0x0000000000000000      0x0000000000000021
    key+0x30: 0x0000000000000000      0x0000000000000000 
    
    memo[-1] points to [key+0x10]
```

1. Fill out tcache 0x20 by calling `Add(size=0x18, offset=0x88)` 7 times (This will not increase id since size > offset).
2. Changing key as above.
3. `Delete memo[-1]`.
4. Call `malloc_consolidate` by using `Add(size=0x448, offset=0x500)`. `malloc(0x448)` will call `malloc_consolidate` to send fastbins into unsorted bin. But due to we gave offset > size, `free()` gets called consecutive, sending chunks in unsorted bin into to their respective bins. In this case, small bin 0x20.
5. We get the small bin address in the key.
6. If we partial overwrite the key right now that it is still in small bin, it'll mess up `fd` and `bk`, and we'll not be able to continue. So, we need to allocate it out of small bin before leaking. However, `calloc` clears the address that we want QAQ.
7. Luckily, if the chunk is mmaped, `calloc` assumes that it is '\x00' by default and doesn't `memset` it (`perturb_byte` is a global variable with default 0). Therefore, we can use `Change key` to set the size to `0x22` and bypass `calloc` clearing the content! (The documentation says the bit indicating whether the chunk is mmaped of not is 0x4, but in the code it actually is 0x2. I don't know freaking why).
8. By `Add(size=0x18, offset=0x00, content='a')` we will get a memo on the stack with libc address in it! (This will increase id by 1)

```
https://elixir.bootlin.com/glibc/glibc-2.27/source/malloc/malloc.c#L3461

  /* Two optional cases in which clearing not necessary */
  if (chunk_is_mmapped (p))
    {
      if (__builtin_expect (perturb_byte, 0))
        return memset (mem, 0, sz);

      return mem;
    }
```

* In order to restore the libc value after partial overwriting and guessing right a byte, we just have to `Delete memo[0]` and proceed to step 4~8 as above.
* The problem is that to leak the address byte by byte. It requires us to use 5 times `Add`. Recall that we only have 5 times, this will leave us no `Add` anymore for hijacking control flow.
* The magic is: On the first time that we get a memo with libc address in it. We could give `offset=0x8, content='\x00'*8`. Partial overwrite the first byte to 0x1 with `Change key`. And we could actually `Delete memo[-5]`!
* The upper part of the libc address becomes the `id` field of memo so that we could guess the `id` from 0x7d00 to 0x7fff. If we guessed wrong, the program shows `Entry not found...` and if we guessed right, it just calls `free(0)` and nothing happens!
* By doing this, we could leak the upper 4 bytes plus 1 byte of the lower 4 bytes of libc address. Leaving us to only have to leak 2 more bytes. That's a total of calling `Add` successfully 3 times with 2 times left. And we already got the libc address leaked.

* After having libc, hijacking control flow isn't that hard. We just have to call `Add(size=0x448, offset=0x0)` to trigger `malloc_consolidate` again. This time we give offset < size which will cost us one time, but it doesn't calls `free`, so the chunk stays in the unsorted bin instead of the small bin.
* Modify the chunk size to a big value with `Change key` and then allocate the same size with the right offset so that we overwrite the return address of main but not canary. Write the return address to `one_gadget`. This will be the last `Add`.
* Exit the program to get shell :)
