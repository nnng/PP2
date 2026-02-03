n = int(input())

doramas = {}

for i in range(n):
    name, k = input().split()
    k = int(k)

    if name in doramas:
        doramas[name] += k
    else:
        doramas[name] = k

for name in sorted(doramas):
    print(name, doramas[name])
