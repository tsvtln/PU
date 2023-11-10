r = "V"  # example value
v = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
    "": 0
}
n = sum(v[r[i]] if v[r[i+1:i+2]] <= v[r[i]] else -v[r[i]] for i in range(len(r)))

print(n)
