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

async def to_encrypt(data):
    encrypted = await fernet.encrypt(json.dumps(data).encode())
    with await open("data.enc", "wb") as f:
        await f.write(encrypted)


async def to_decrypt(file):
    with await open(file, "rb") as f:
        encrypted = await f.read()

    data = await json.loads(fernet.decrypt(encrypted).decode())
    return data