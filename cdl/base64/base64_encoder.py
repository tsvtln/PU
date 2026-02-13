import base64

with open("to_encode.txt", "r") as f:
    content = f.read()

# Convert text to UTF-16LE and base64 encode
encoded_b64 = base64.b64encode(content.encode("utf-16le")).decode("ascii")

print(encoded_b64)