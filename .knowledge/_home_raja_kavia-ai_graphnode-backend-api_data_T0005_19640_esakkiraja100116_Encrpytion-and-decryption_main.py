{"is_source_file": true, "format": "Python", "description": "This file contains code for encrypting and decrypting a string using the Fernet symmetric encryption method from the cryptography library.", "external_files": ["cryptography.fernet"], "external_methods": ["Fernet.generate_key", "Fernet.encrypt", "Fernet.decrypt"], "published": [], "classes": [], "methods": [], "calls": ["cryptography.fernet.Fernet.generate_key", "cryptography.fernet.Fernet.encrypt", "cryptography.fernet.Fernet.decrypt"], "search-terms": ["encryption", "decryption", "Fernet", "cryptography"], "state": 2, "ctags": ["decMessage: /^decMessage = fernet.decrypt(encMessage).decode()$/;\"", "encMessage: /^encMessage = fernet.encrypt(message.encode())$/;\"", "fernet: /^fernet = Fernet(key)$/;\"", "key: /^key = Fernet.generate_key()$/;\"", "message: /^message = \"Esakkiraja\"$/;\""], "filename": "/home/raja/kavia-ai/graphnode-backend-api/data/T0005/19640/esakkiraja100116/Encrpytion-and-decryption/main.py", "hash": "a86042154efa10187158ee5e13ab19c0", "format-version": 3, "code-base-name": "b3517wc"}