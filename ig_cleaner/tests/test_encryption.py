import unittest
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.encrypt import encrypt_data, decrypt_data
from app.config import ENCRYPTION_KEY

class TestEncryption(unittest.TestCase):

    def test_encryption_decryption_cycle(self):
        """
        Tests that data encrypted can be successfully decrypted back to its original form.
        """
        original_data = "mysecretpassword123"

        # Ensure the encryption key is set for the test environment
        self.assertIsNotNone(ENCRYPTION_KEY, "ENCRYPTION_KEY must be set for tests.")

        encrypted_data = encrypt_data(original_data)
        self.assertIsNotNone(encrypted_data)
        self.assertNotEqual(original_data, encrypted_data)

        decrypted_data = decrypt_data(encrypted_data)
        self.assertEqual(original_data, decrypted_data)

    def test_empty_string(self):
        """
        Tests that encrypting and decrypting an empty string works correctly.
        """
        original_data = ""
        encrypted_data = encrypt_data(original_data)
        self.assertEqual(original_data, encrypted_data) # Should return empty string

        decrypted_data = decrypt_data(encrypted_data)
        self.assertEqual(original_data, decrypted_data)

if __name__ == '__main__':
    unittest.main()
