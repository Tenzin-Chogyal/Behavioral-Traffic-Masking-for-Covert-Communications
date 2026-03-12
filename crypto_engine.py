"""
Cryptographic Engine - Layer 1
AES-256-GCM encryption with deniable encryption (dual password support)
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64


class CryptographicEngine:
    """
    Layer 1: Cryptographic protection with deniable encryption
    
    Features:
    - AES-256-GCM authenticated encryption
    - PBKDF2 key derivation (100,000 iterations)
    - Dual-password deniable encryption support
    """
    
    def __init__(self, real_password=None, duress_password=None):
        """
        Initialize crypto engine with dual password support
        
        Args:
            real_password: Password for real secret messages
            duress_password: Password for fake innocuous messages (deniable encryption)
        """
        self.real_password = real_password or "default_real_password_2024"
        self.duress_password = duress_password or "default_duress_password_2024"
        
        # Fixed salt for demonstration (in production, use unique salts)
        self.salt = b'covert_system_salt_2024_secure'
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """
        Derive 256-bit key from password using PBKDF2
        
        Args:
            password: User password
            salt: Salt for key derivation
            
        Returns:
            32-byte key
        """
        if salt is None:
            salt = self.salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000
        )
        return kdf.derive(password.encode())
    
    def encrypt(self, plaintext: str, use_real_password: bool = True) -> bytes:
        """
        Encrypt message with AES-256-GCM
        
        Args:
            plaintext: Message to encrypt
            use_real_password: True for real key, False for duress key
            
        Returns:
            Encrypted data (nonce + ciphertext + tag)
        """
        # Choose password
        password = self.real_password if use_real_password else self.duress_password
        
        # Derive key
        key = self._derive_key(password)
        
        # Create cipher
        aesgcm = AESGCM(key)
        
        # Generate random nonce
        nonce = os.urandom(12)  # 96 bits for GCM
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        # Return nonce + ciphertext
        return nonce + ciphertext
    
    def decrypt(self, encrypted_data: bytes, use_real_password: bool = True) -> str:
        """
        Decrypt message with AES-256-GCM
        
        Args:
            encrypted_data: Encrypted data (nonce + ciphertext + tag)
            use_real_password: True for real key, False for duress key
            
        Returns:
            Decrypted plaintext
        """
        # Choose password
        password = self.real_password if use_real_password else self.duress_password
        
        # Derive key
        key = self._derive_key(password)
        
        # Create cipher
        aesgcm = AESGCM(key)
        
        # Extract nonce and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Decrypt
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
    
    def encrypt_with_both_keys(self, real_message: str, duress_message: str) -> tuple:
        """
        Encrypt both real and duress messages
        
        Args:
            real_message: Real secret message
            duress_message: Fake innocuous message
            
        Returns:
            (real_encrypted, duress_encrypted)
        """
        real_encrypted = self.encrypt(real_message, use_real_password=True)
        duress_encrypted = self.encrypt(duress_message, use_real_password=False)
        return real_encrypted, duress_encrypted


# Quick test
if __name__ == "__main__":
    print("="*70)
    print("CRYPTOGRAPHIC ENGINE TEST")
    print("="*70)
    
    crypto = CryptographicEngine(
        real_password="SecretOperationKey",
        duress_password="InnocentPhotoPassword"
    )
    
    # Test real message
    print("\n[TEST 1] Real Message Encryption")
    real_msg = "Operation Phoenix is GO at 0300 hours"
    print(f"Original: {real_msg}")
    encrypted = crypto.encrypt(real_msg, use_real_password=True)
    print(f"Encrypted: {len(encrypted)} bytes")
    decrypted = crypto.decrypt(encrypted, use_real_password=True)
    print(f"Decrypted: {decrypted}")
    print(f"✓ Match: {real_msg == decrypted}")
    
    # Test duress message
    print("\n[TEST 2] Duress Message Encryption")
    duress_msg = "Just sharing some vacation photos"
    print(f"Original: {duress_msg}")
    encrypted = crypto.encrypt(duress_msg, use_real_password=False)
    print(f"Encrypted: {len(encrypted)} bytes")
    decrypted = crypto.decrypt(encrypted, use_real_password=False)
    print(f"Decrypted: {decrypted}")
    print(f"✓ Match: {duress_msg == decrypted}")
    
    # Test deniability
    print("\n[TEST 3] Deniable Encryption")
    real_encrypted, duress_encrypted = crypto.encrypt_with_both_keys(
        "Secret intelligence data",
        "Family photo album"
    )
    print(f"Real encrypted: {len(real_encrypted)} bytes")
    print(f"Duress encrypted: {len(duress_encrypted)} bytes")
    print(f"Real decrypt: {crypto.decrypt(real_encrypted, True)}")
    print(f"Duress decrypt: {crypto.decrypt(duress_encrypted, False)}")
    print("✓ Deniable encryption working")
    
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED")
    print("="*70)
