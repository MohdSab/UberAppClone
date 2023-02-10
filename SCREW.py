end = {'DRIVER': {'bob': [1, 2, 3, 4, 5], 'mar': [6, 7, 8, 9], 'lucky': [2]},
       'PASS': {'fag': [11, 12, 13, 14, 15], 'jack': [16, 17, 18, 19]}}

total = 0

print(end['DRIVER'].values())

count = len(end['DRIVER'].keys())
print(count)

for value in end['DRIVER'].values():
    if len(value) >= 2:
        for i in range(len(value) - 1):
            curr = value[i]
            stop = value[i + 1]
            total += stop - curr
            print(f'{curr} + {stop}')

print(total/count)
