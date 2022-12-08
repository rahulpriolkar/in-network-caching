db = {}
file = open("KeyVal.txt", "r+")
for line in file:
    key, val = line.split()
    db[int(key)] = int(val)
file.close()

vals= {}
count = 0
file = open("h1_received.txt", "r+")
for line in file:
    line = line.split()
    key = line[1]
    val = line[4]
    if db[int(key)] != int(val):
        count += 1
        print("ID = ", line[0] ," key = ", key, " db_val = ", db[int(key)], " val = ", int(val))
        print("Mismatch")
file.close()
print(count)

