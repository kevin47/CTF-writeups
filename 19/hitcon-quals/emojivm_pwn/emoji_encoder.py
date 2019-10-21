func_emojis = {
    "PUSH": "⏬",
    "POP": "🔝",
    "ADD": "➕",
    "AND": "👫",
    "SUB": "➖",
    "MUL": "❌",
    "ALLOC": "🆕",
    "FREE": "🆓",
    "GETVAL": "📤",
    "SETVAL": "📥",
    "ITOA": "🔢",
    "JMPIF": "🈶",
    "JMPNOTIF": "🈚",
    "JMP": "🚀",
    "NOP": "🈳",
    "PRINT_STR": "🔡",
    "READ_HEAP": "📄",
    "WRITE_HEAP": "📝",
}

val_emojis = {
        0: "😀",
        1: "😁",
        2: "😂",
        3: "🤣",
        4: "😜",
        5: "😄",
        6: "😅",
        7: "😆",
        8: "😉",
        9: "😊",
        10: "😍"
}
val_emojis = dict(sorted(val_emojis.items(), reverse=True))

def push(n):
    assert n < 100
    if n > 10:
        code = 'PUSH 10 ' + f'PUSH {n // 10} ' + 'MUL '
        if n % 10:
            code += f'PUSH {n % 10} ' + 'ADD '
    else:
        code = f'PUSH {n} '
    return code

def alloc(n):
    return push(n) + 'ALLOC '

def getval(buf, i=0):
    return push(i) + push(buf) + 'GETVAL '

def setval(buf, i=0, val=None):
    return (push(val) if val is not None else '') + push(i) + push(buf) + 'SETVAL '

def inc(buf):
    return getval(buf) + 'PUSH 1 ' + 'ADD ' + setval(buf)

def out(encode=False):
    return setval(output, 0, 0) + setval(output, 1, 0) + setval(output, 2, 0) + \
        ('ITOA ' if encode else '') + setval(output) + 'PUSH 0 ' + 'PRINT '

example_code = """
# output
{alloc(3)}

# i
{alloc(1)}

# j
{alloc(1)}

:iloop:
{inc(i)}

{setval(j, 0, 0)}

:jloop:
PUSH 0
PUSH 0
PUSH 0
PUSH 0

{inc(j)}

{getval(i)}
{out(True)}
{push(32)}
{out()}
{push(42)}
{out()}
{push(32)}
{out()}
{getval(j)}
{out(True)}
{push(32)}
{out()}
{push(61)}
{out()}
{push(32)}
{out()}
{getval(i)}
{getval(j)}
MUL
{out(True)}
{push(10)}
{out()}

{getval(j)}
PUSH 9
SUB
*:jloop:
JMPIF

{getval(i)}
PUSH 9
SUB
*:iloop:
JMPIF
"""


def emoji_compile(code):
    code = '\n'.join(line for line in code.split('\n') if not line.startswith('#'))

    label_lookup = {}

    position = 0
    for line in code.split('\n'):
        if line.startswith('*'):
            position += 30
        elif line.startswith(':'):
            label_lookup[line] = position
        else:
            position += len(simple_compile(line))

    print(label_lookup)

    result = ''
    for line in code.split('\n'):
        if line.startswith('*'):
            result += simple_compile(push(label_lookup[line[1:]])).ljust(30, func_emojis['NOOP'])
        elif not line.startswith(':'):
            result += simple_compile(line)

    print(result)
    return result


def simple_compile(code):
    for func, emoji in func_emojis.items():
        code = code.replace(func, emoji)
    for val, emoji in val_emojis.items():
        code = code.replace(str(val), emoji)
    code = code.replace(' ', '').replace('\n', '')
    return code

code = "" 

with open("emoji_asm","r") as fp:
    code = fp.read() 

with open("generated_code", "w") as f:
    f.write(simple_compile(code))
