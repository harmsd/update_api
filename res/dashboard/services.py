from cryptography.fernet import Fernet
import json

key = "jq71SphIIy-2IbrZ_6UupEcyd6xuCLdlDu8hTWC0has="

fernet = Fernet(key)

# data = {
#     'username': "admin",
#     "password": "super_secret_123",
#     "api_key": "my_api_key"
# }

# encrypted = fernet.encrypt(json.dumps(data).encode())

# with open("data.enc", "wb") as f:
#     f.write(encrypted)


with open("data.enc", "rb") as f:
    encrypted = f.read()

data = json.loads(fernet.decrypt(encrypted).decode())

print(data)