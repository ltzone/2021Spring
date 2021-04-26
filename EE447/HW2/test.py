K = 29
E_table = []
for i in range(K+1):
    E_table.append([0 for j in range(K+1)])

for i in range(K+1):
    E_table[i][K] = 100

for i in range(K-1,-1,-1):
    for j in range(K-1,-1,-1):
        E_table[i][j] = - 1 + 0.51 * E_table[i][j+1] + 0.49 * E_table[i+1][j]

for i in range(K):
    print(29-i, E_table[1+i][i])

print (E_table)