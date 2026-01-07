from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os
import base64
import numpy as np
from typing import Tuple
from app.config import settings


class EncryptionService:
    """Service for encrypting/decrypting face embeddings using AES-256-GCM"""

    def __init__(self):
        # Derive a 32-byte key from SECRET_KEY
        secret_key = settings.secret_key.encode('utf-8')[:32].ljust(32, b'0')
        self.aesgcm = AESGCM(secret_key)
        self.key_id = settings.encryption_key_id

    def encrypt_embedding(self, embedding: np.ndarray) -> Tuple[bytes, str]:
        """
        Encrypt a face embedding vector (512-dim float32 array)
        
        Returns:
            Tuple of (encrypted_bytes, key_id)
        """
        # Convert numpy array to bytes
        embedding_bytes = embedding.astype(np.float32).tobytes()
        
        # Generate a random nonce (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # Encrypt
        ciphertext = self.aesgcm.encrypt(nonce, embedding_bytes, None)
        
        # Prepend nonce to ciphertext
        encrypted_data = nonce + ciphertext
        
        return encrypted_data, self.key_id

    def decrypt_embedding(self, encrypted_data: bytes, key_id: str) -> np.ndarray:
        """
        Decrypt an encrypted face embedding
        
        Returns:
            numpy array (512-dim float32)
        """
        # Extract nonce (first 12 bytes)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Decrypt
        embedding_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        
        # Convert bytes back to numpy array
        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        
        return embedding

    def encrypt_bytes(self, data: bytes) -> Tuple[bytes, str]:
        """Encrypt arbitrary bytes"""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        encrypted_data = nonce + ciphertext
        return encrypted_data, self.key_id

    def decrypt_bytes(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt arbitrary bytes"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)


# Singleton instance
encryption_service = EncryptionService()

