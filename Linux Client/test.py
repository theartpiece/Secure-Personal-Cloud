
def gen():
	for i in range(10):
		yield i*i
		print(i)

for x in gen():
	print(x)