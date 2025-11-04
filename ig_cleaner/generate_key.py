import secrets
import os

def generate_secure_key():
    """
    Generates a cryptographically secure, 32-byte key suitable for AES encryption.
    """
    return secrets.token_hex(16)

def main():
    """
    Main function to generate a key and provide instructions to the user.
    """
    new_key = generate_secure_key()

    print("\n--- Secure Encryption Key Generation ---")
    print(f"\nGenerated Key: {new_key}")
    print("\nThis is a secure, 32-byte key suitable for your .env file.")
    print("\nInstructions:")
    print("1. Copy the generated key above.")
    print("2. Open or create your `.env` file in the project's root directory.")
    print(f"3. Add or update the ENCRYPTION_KEY variable like this:\n")
    print(f"   ENCRYPTION_KEY=\"{new_key}\"")
    print("\n----------------------------------------\n")

if __name__ == "__main__":
    # Ensure the script is run from the project root for clarity on .env location
    if not os.path.exists('ig_cleaner'):
        print("Warning: This script should be run from the root directory of the 'ig_cleaner' project.")
    main()
