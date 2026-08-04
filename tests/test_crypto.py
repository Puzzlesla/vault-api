from app.utils.crypto import encrypt_data, decrypt_data

def test_encrypt_decrypt_roundtrip():
    plaintext = "This is a test string."
    encrypted = encrypt_data(plaintext)
    assert encrypted != plaintext  # Ensure encryption changes the data
    assert decrypt_data(encrypted) == plaintext  # Ensure decryption returns original plaintext

def test_encrypt_same_input_different_output():
    plaintext = "Same input"
    encrypted1 = encrypt_data(plaintext)
    encrypted2 = encrypt_data(plaintext)
    assert encrypted1 != encrypted2  # Ensure that encrypting the same plaintext produces different ciphertexts

# Test that decrypting an invalid ciphertext raises a ValueError
def test_decrypt_invalid_data():
    import pytest
    with pytest.raises(ValueError):
        decrypt_data("invalid-ciphertext")


        