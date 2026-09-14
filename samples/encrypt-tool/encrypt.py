#!/usr/bin/env python3
"""File encryption tool — AES-256-GCM.

Encrypts/decrypts files with a passphrase-derived key. Uses AES-256-GCM
(authenticated encryption — tamper detection built in).

Usage:
    python encrypt.py encrypt secret.txt
    python encrypt.py decrypt secret.txt.enc
"""
from __future__ import annotations
import argparse
import hashlib
import os
import sys
from getpass import getpass

# AES-256-GCM via cryptography library (the standard for Python crypto)
# If cryptography isn't installed, fall back to a pure-Python XOR cipher
# (warning: XOR is NOT secure — for demonstration only)
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("Warning: 'cryptography' not installed. Using insecure XOR fallback.", file=sys.stderr)
    print("Install with: pip install cryptography", file=sys.stderr)


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive 32-byte key from passphrase + salt using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=600_000, dklen=32)


def encrypt_file(path: str, passphrase: str) -> str:
    """Encrypt a file. Returns path to encrypted file."""
    with open(path, "rb") as f:
        plaintext = f.read()

    if HAS_CRYPTO:
        # AES-256-GCM (authenticated)
        salt = os.urandom(16)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        key = derive_key(passphrase, salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        # Pack: salt (16) + nonce (12) + ciphertext + tag (16, included in ciphertext)
        packed = b"AES1" + salt + nonce + ciphertext
    else:
        # Insecure XOR fallback (demonstration only)
        salt = os.urandom(16)
        key = derive_key(passphrase, salt)
        ciphertext = bytes(b ^ key[i % len(key)] for i, b in enumerate(plaintext))
        packed = b"XOR1" + salt + ciphertext

    out_path = path + ".enc"
    with open(out_path, "wb") as f:
        f.write(packed)
    return out_path


def decrypt_file(path: str, passphrase: str) -> str:
    """Decrypt a file. Returns path to decrypted file."""
    with open(path, "rb") as f:
        packed = f.read()

    magic = packed[:4]
    if magic not in (b"AES1", b"XOR1"):
        raise ValueError("Not an encrypted file (missing magic bytes)")

    salt = packed[4:20]
    if magic == b"AES1":
        nonce = packed[20:32]
        ciphertext = packed[32:]
        key = derive_key(passphrase, salt)
        aesgcm = AESGCM(key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            print("Error: wrong passphrase or corrupted file.", file=sys.stderr)
            sys.exit(1)
    else:  # XOR fallback
        ciphertext = packed[20:]
        key = derive_key(passphrase, salt)
        plaintext = bytes(b ^ key[i % len(key)] for i, b in enumerate(ciphertext))

    if path.endswith(".enc"):
        out_path = path[:-4]
    else:
        out_path = path + ".dec"
    with open(out_path, "wb") as f:
        f.write(plaintext)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="AES-256-GCM file encryption")
    ap.add_argument("action", choices=["encrypt", "decrypt"], help="action to perform")
    ap.add_argument("file", help="file to encrypt or decrypt")
    ap.add_argument("--passphrase", "-p", help="passphrase (will prompt if not provided)")
    args = ap.parse_args()

    passphrase = args.passphrase or getpass("Passphrase: ")
    if not passphrase:
        print("Error: passphrase required", file=sys.stderr)
        sys.exit(1)

    if args.action == "encrypt":
        out = encrypt_file(args.file, passphrase)
        print(f"Encrypted: {args.file} → {out}")
    else:
        if not args.file.endswith(".enc"):
            print("Error: decrypt requires a .enc file", file=sys.stderr)
            sys.exit(1)
        out = decrypt_file(args.file, passphrase)
        print(f"Decrypted: {args.file} → {out}")


if __name__ == "__main__":
    main()
