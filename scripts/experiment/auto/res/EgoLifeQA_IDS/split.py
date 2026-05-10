LEN,N=500,4
for n in range(N): open(f"{chr(ord('a') + n)}.txt", "w").write(",".join([str(i+1) for i in range(n*(LEN//N), (n+1)*(LEN//N))]))