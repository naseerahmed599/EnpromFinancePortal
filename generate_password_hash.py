#!/usr/bin/env python3
"""
Password Hash Generator for ENPROM Finance Portal
Generate secure SHA-256 hashes for user passwords
"""

import hashlib
import getpass


def hash_password(password: str) -> str:
    """Generate SHA-256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()


def main():
    print("=" * 60)
    print("ENPROM Finance Portal - Password Hash Generator")
    print("=" * 60)
    print("\nThis tool generates secure SHA-256 hashes for passwords.")
    print("Use these hashes in your secrets.toml file for better security.\n")
    
    while True:
        # Get password from user (hidden input)
        password = getpass.getpass("Enter password to hash (or 'quit' to exit): ")
        
        if password.lower() == 'quit':
            print("\nGoodbye!")
            break
        
        if not password:
            print("❌ Password cannot be empty!\n")
            continue
        
        # Generate hash
        password_hash = hash_password(password)
        
        # Display result
        print("\n" + "=" * 60)
        print("✅ Password Hash Generated:")
        print("=" * 60)
        print(f"\nOriginal Password: {password}")
        print(f"SHA-256 Hash: {password_hash}")
        print("\n📋 Copy this hash to your secrets.toml file:")
        print(f'password = "{password_hash}"')
        print("=" * 60 + "\n")
        
        # Ask if user wants to generate another
        another = input("Generate another hash? (y/n): ")
        if another.lower() != 'y':
            print("\nGoodbye!")
            break
        print()


if __name__ == "__main__":
    main()
