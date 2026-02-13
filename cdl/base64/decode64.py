import base64

with open("encoded.txt") as f:
    b64data = f.read()

decoded = base64.b64decode(b64data).decode("utf-16le")

print(decoded)