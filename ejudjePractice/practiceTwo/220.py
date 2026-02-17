n = int(input())

document = {}

for i in range(n):
    command = input().split()

    if command[0] == "set":
        key = command[1]
        value = command[2]
        document[key] = value

    elif command[0] == "get":
        key = command[1]
        if key in document:
            print(document[key])
        else:
            print(f"KE: no key {key} found in the document")
