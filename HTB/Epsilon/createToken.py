import jwt

# Payload
payload = {"username": "admin"}

# Secret key
secret = 'RrXCv`mrNe!K!4+5`wYq'

# Tạo token
token = jwt.encode(payload, secret, algorithm="HS256")

print(token)