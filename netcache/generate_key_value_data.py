import sys
import random

def gen(start, end):
    db = []
    for i in range(start, end):
        db.append({i: random.randint(0, 2**10)})
    write(db)
    return db

def write(db):
    file = open("KeyVal.txt", "w+")
    for obj in db:
        for key, val in obj.items():
            file.write("{} {}\n".format(key, val))
    file.close()

def read():
    file = open("KeyVal.txt", "r+")
    db = {}
    for line in file:
        line = line.split()
        key = int(line[0])
        val = int(line[1])
        db[key] = val
    return db

if __name__ == "__main__":
    db = gen(int(sys.argv[1]), int(sys.argv[2]))
    write(db) 
    print(read())
