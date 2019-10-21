# Crypto in the shell
* It's AES_CBC.
* There is an index out of bounds vulnerability when inputting offset. Thus we can encrypt any address and print the encrypted result with unknown KEY and null IV.
* It turns out that the key is just before the buffer. We can encrypt it with itself. Since the result is printed, now we have AES_CBC encryption with known key.
* Now that we have key, we can encrypt an address, print its value and decrypt it locally to leak. We leak `libc address`, `environ pointer (stack address)` using this method.
* We only have 32 encryptions in one connection. And it is really hard to achieve arbitrary write this way. Luckily, the `i` for the `for` loop is on stack, we can encrypt it to make it a big negative integer, thus having nearly unlimited number of encryption (It has 1/2 probability to fail because `i` could be encrypted to a big positive integer).
* Bypassed the time limit, we could keep encrypting the same address until the first byte becomes the value we desired, shift by one byte and continue doing the same thing. This gives us a nearly arbitrary write.
* Overwrite main's return address to `one_gadget` and `environ` to its original value (it has been overwritten to a junk value since we leaked it).
* Overwrite `i` until it becomes a big positive integer. Causing main to return and trigger `one_gadget`.
