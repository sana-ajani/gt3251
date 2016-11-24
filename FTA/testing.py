b = bytearray("hell")
b.append(10)
for i in range(0, len(b), 5):
	print [b[i], b[i+1], b[i+2], b[i+3], b[i+4]]
if 10 in b:
	print True

a = bytearray("he")
a += bytearray("ll")

for i in range(len(a)):
	print a[i]

