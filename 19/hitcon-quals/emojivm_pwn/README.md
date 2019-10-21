# EmojiVM (pwn)
* Thanks to Zion for helping me to reverse and write the encoder.
* For all instructions except for `pop`, there isn't any check for stack underflow (Fake stack on the bss, not the real stack).
* Since the heap pointers from `alloc` are also on the bss, before the fake stack, we could underflow the stack and modify it.
* Allocate two heaps, since their gap will be the same even with ASLR, use `add` to modify one pointer such that it becomes the same address as the other one. Causing double free/used after free vulnerability.
* From now on, it's just basic tcache poisoning.
