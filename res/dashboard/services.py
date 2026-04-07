from cryptography.fernet import Fernet
import json

from fastapi import HTTPException, UploadFile

key = "jq71SphIIy-2IbrZ_6UupEcyd6xuCLdlDu8hTWC0has="

fernet = Fernet(key)

# data = {
#   "organization": {
#     "name": "ООО «ТехноСофт»",
#     "inn": "7712345678",
#     "email": "info@technosoft.ru",
#     "tariff": "Профессиональный",
#     "licenses": 25,
#     "expiry": "31.12.2026"
#   },

#   "checksum": {
#     "algorithm": "SHA-256",
#     "value": "a3f5c2e1b7d94082ef3120c6a8b5d7f9e4c1023ab8d7e6f5c4b3a2910e8f7d6c"
#   },
  
#   "host": {
#     "hostname": "10.0.1.42",
#     "os": "Windows Server 2022",
#     "mac": "3C:52:A1:4B:7F:2D",
#     "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
#     "comment": "Основной сервер приложений, стойка A3"
#   }
# }


def to_encrypt(data):
    encrypted = fernet.encrypt(json.dumps(data).encode())

    with open("data.enc", "wb") as f:
        f.write(encrypted)


async def to_decrypt(file: UploadFile):
    if not file.filename.lower().endswith(".enc"):
        raise HTTPException(status_code=400, detail=".enc files")
    
    encrypted = await file.read()

    if not encrypted:
        raise HTTPException(status_code=400, detail="file is empty")

    try:
        decrypte = fernet.decrypt(encrypted)
        data = json.loads(decrypte.decode())

    except Exception:
        raise HTTPException(status_code=400, detail="Couldn't decrypt the file")
    data = json.loads(fernet.decrypt(encrypted).decode())

    return data
