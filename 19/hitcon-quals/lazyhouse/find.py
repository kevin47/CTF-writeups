from gmpy2 import powmod

def gcd(a, b):
  while b: a, b = b, a % b
  return a

x = 218/2
m = 2**64 / 2

for y in range(116630/2):
  a = y * powmod(x, -1, m) % m
  if a < 0x8000000000000000:
    print a
    assert a*218 % (2**64) < 116630
