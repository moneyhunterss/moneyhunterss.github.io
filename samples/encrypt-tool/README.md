# File Encryption Tool — AES-256-GCM

Encrypt and decrypt files with a passphrase. Uses AES-256-GCM (authenticated
encryption — tamper detection built in).

## Features

- AES-256-GCM (NIST-standard authenticated encryption)
- PBKDF2-HMAC-SHA256 key derivation (600,000 iterations — slow-hash against brute force)
- Random 16-byte salt + 12-byte nonce per file (unique keys per encryption)
- Magic byte header (`AES1`) for file format detection
- Falls back to XOR if `cryptography` not installed (insecure, demo only)

## Quick start

```bash
pip install cryptography

# Encrypt a file (will prompt for passphrase)
python encrypt.py encrypt secret.txt

# Decrypt (will prompt for passphrase)
python encrypt.py decrypt secret.txt.enc

# Pass passphrase via flag (less secure — ends up in shell history)
python encrypt.py encrypt secret.txt --passphrase "my-secret-key"
```

## How it works

1. Generate 16-byte random salt
2. Derive 32-byte key from passphrase + salt via PBKDF2-HMAC-SHA256 (600k iterations)
3. Generate 12-byte random nonce
4. Encrypt plaintext with AES-256-GCM (returns ciphertext + 16-byte auth tag)
5. Write to file: `AES1` (4 bytes magic) + salt (16) + nonce (12) + ciphertext + tag

To decrypt:
1. Read salt + nonce + ciphertext + tag from file
2. Derive key from passphrase + salt
3. AES-256-GCM decrypt (verifies auth tag — fails if passphrase wrong OR file tampered)

## Security notes

- **Passphrase strength matters.** AES-256 is unbreakable, but a 6-char passphrase falls to a 6-GPU rig in hours. Use 16+ chars.
- **PBKDF2 600k iterations** slows brute force by ~600kx. Still vulnerable to offline attacks if your passphrase is weak.
- **Authenticated encryption** (GCM mode) means tampering is detected. If someone modifies the encrypted file, decryption fails.
- For high-value targets, consider Argon2id instead of PBKDF2 (memory-hard, GPU-resistant). I'd add this for $200+.

## Use cases

- Encrypt sensitive client data at rest
- Secure backups before cloud upload
- Protect credentials / API keys in config files
- P2P file sharing with shared passphrase

## Tech

- Python 3.10+
- `cryptography` (PyCA — the standard Python crypto library)
- `hashlib.pbkdf2_hmac` — key derivation
- `os.urandom` — cryptographically secure RNG

## License

MIT — for legal encryption of your own data. Don't use to evade lawful decryption orders.
