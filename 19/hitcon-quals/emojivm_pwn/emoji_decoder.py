#!/usr/bin/env python

STACK = []
STACK_PTR = 0
instruction_ptr = 0
SINGLE_STEP=False

ALLOC_LIST = [None]*10


class size_alloc:
    size = None
    space = None

    def __init__(self, size):
        self.size = size
        self.space = [0]*(size+1)


def no_op():
    pass

def add():
    
    val_1 = STACK.pop()
    val_2 = STACK.pop()

    print("ADD:", val_1, "+", val_2)
    STACK.append(val_1 + val_2)

def sub():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("SUB:", val_1, "-", val_2)
    STACK.append(val_1 - val_2)

def mult():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("MULT:", val_1, "*", val_2)
    STACK.append(val_1 * val_2)

def mod():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("MOD:", val_1, "%", val_2)
    STACK.append(val_1 % val_2)

def xor():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("XOR:", val_1, "^", val_2)
    STACK.append(val_1 ^ val_2)

def logical_and():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("AND:", val_1, "&", val_2)
    STACK.append(val_1 & val_2)

def less_than():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("LESSTHAN:", val_1, "<", val_2)
    STACK.append(val_1 < val_2)

def eql():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    print("EQL:", val_1, "==", val_2)
    STACK.append(val_1 == val_2)

def jmp():
    global instruction_ptr
    val_1 = STACK.pop()
    instruction_ptr = val_1-1
    print("JMP:", val_1)

def jmp_if():
    global instruction_ptr
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    if val_2:
        instruction_ptr = val_1-1
    print("JIF:", val_2)

def jmp_not_if():
    global instruction_ptr
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    if not val_2:
        instruction_ptr = val_1-1
    print("JIF NOT:", val_2)

def push():
    pass

def pop():
    pass

def alloc():
    size = STACK.pop()
    for i in range(len(ALLOC_LIST)):
        if not ALLOC_LIST[i]:
            ALLOC_LIST[i] = size_alloc(size)
            print("ALLOCATING", ALLOC_LIST[i])
            break

def set_val():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    val_3 = STACK.pop()
    if (val_1 >= 0 and val_1 < 10) or not ALLOC_LIST[val_1]:
        bloc = ALLOC_LIST[val_1]
        if bloc and bloc.size >= 0 and val_2 < bloc.size :
            bloc.space[val_2] = val_3
            print("SETTING ALLOC:", val_1, "IDX", val_2, "TO", val_3)
        

def print_string():
    val_1 = STACK.pop()
    if (val_1 >= 0 and val_1 < 10) or not ALLOC_LIST[val_1]:
        bloc = ALLOC_LIST[val_1]
        print_str = ''
        for x in bloc.space:
            if x == 0:
                break
            print_str += chr(x)
        print("AFTER")
        print(len(print_str))
        print(repr(print_str))
        print(print_str[0:len(print_str)-31], end='')

def read():
    global SINGLE_STEP
    #SINGLE_STEP = True
    val_1 = STACK.pop()
    if (val_1 >= 0 and val_1 < 10) or not ALLOC_LIST[val_1]:
        bloc = ALLOC_LIST[val_1]
        if bloc:
            inp = 'ABCD-FGHI-KLMN-PQRS-UVWX\n'
            #inp = input()
            #print("GOT INPUT????")
            for x in range(len(inp[:bloc.size])):
                bloc.space[x] = ord(inp[x])


def get_val():
    val_1 = STACK.pop()
    val_2 = STACK.pop()
    if (val_1 >= 0 and val_1 < 10) or not ALLOC_LIST[val_1]: 
        bloc = ALLOC_LIST[val_1]
        print("ATTEMPTING TO GET VAL", bloc.space)
        if bloc and val_2 >= 0 and val_2 < bloc.size:
            STACK.append(bloc.space[val_2])

def stop():
    exit()

emoji_funcs = {
0x1F233: no_op,
0x2795: add,
0x2796: sub,
0x274C: mult,
0x2753: mod,
0x274E: xor,
0x1F46B: logical_and,
0x1F480: less_than,
0x1F4AF: eql,
0x1F680: jmp,
0x1F236: jmp_if,
0x1F21A: jmp_not_if,
0x23EC: push,
0x1F51D: pop,
0x1F4E4: get_val,
0x1F4E5: set_val,
0x1F195: alloc,
0x1F193: 18,
0x1F4C4: read,
0x1F4DD: print_string,
0x1F521: 21,
0x1F522: 22,
0x1F6D1: stop}

emoji_vals = {
0x1F600: 0,
0x1F601: 1,
0x1F602: 2,
0x1F923: 3,
0x1F61C: 4,
0x1F604: 5,
0x1F605: 6,
0x1F606: 7,
0x1F609: 8,
0x1F60A: 9,
0x1F60D: 10}



if __name__ == '__main__':
    #print(emoji_case)
    data = open('chal.evm', 'r').read()
    while instruction_ptr < len(data):
        emoji_val = ord(data[instruction_ptr])
        #if ALLOC_LIST[5]:
        #    if ALLOC_LIST[5].space[0] == 24:
        #        SINGLE_STEP = True
        if instruction_ptr == 7659:
                SINGLE_STEP = True

        if emoji_val in emoji_funcs:
            if SINGLE_STEP:
                #input()
                pass
            try:
                print(data[instruction_ptr], emoji_funcs[emoji_val].__name__)
            except:
                print("ERR: NOT IMPLEMENTED")
                print(data[instruction_ptr], hex(emoji_funcs[emoji_val]))
                exit(-1)

            emoji_funcs[emoji_val]()
            if emoji_funcs[emoji_val].__name__ is 'push':
                instruction_ptr += 1
                emoji_val = ord(data[instruction_ptr])
                val = emoji_vals[emoji_val]
                print("PUSH VAL:", data[instruction_ptr], val)
                STACK.append(val)
            elif emoji_funcs[emoji_val].__name__ is 'pop':
                instruction_ptr += 1
                emoji_val = ord(data[instruction_ptr])
                print(data[instruction_ptr], val)
            else:
                print()
                pass
        print("IDX", instruction_ptr)
        print("STACK:", STACK)
        for i in range(len(ALLOC_LIST)):
            if ALLOC_LIST[i]:
                print("ALLOC:", i)
                print(ALLOC_LIST[i].space)
        instruction_ptr += 1

