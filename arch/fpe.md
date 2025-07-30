Format-preserving encryption (FPE) is a reversible data-masking technique that replaces sensitive information with ciphertext that keeps the same **length, character set and overall structure** as the original plaintext.  This makes it ideal for situations where legacy databases, APIs or downstream applications expect credit-card numbers to stay 16 digits, Social Security numbers to stay 9 digits, or alphanumeric codes to keep the same punctuation and spacing.

Today the dominant algorithms come from the **NIST SP 800-38G** standard:

- **FF1** – a balanced-Feistel design built on AES; supports any radix (digits, letters, unicode) and tweak lengths up to 2⁶⁴ bytes.  
- **FF3-1** – a revised, unbalanced-Feistel construction that replaced the withdrawn FF3; it requires a 7-byte tweak and a domain of at least one million possible values .  

Earlier proposals such as **FF2/FF2.1** and **FF3** have been deprecated due to cryptanalytic attacks .  Outside the NIST portfolio you may still encounter:

- **Hasty Pudding Cipher** – a historical variable-block-size cipher.  
- **VISA FPE** – a counter-mode stream cipher used in some payment HSMs .  
- **FEA-1/FEA-2** – South-Korean national standards.

Open-source implementations of FF1 and FF3-1 are available in C, Go, Java, Python, C#, Node.js and Rust, making it straightforward to adopt FPE for protecting PII while keeping existing schemas intact .



`ff3` itself does **not** provide helpers to create keys or tweaks, so you just have to generate cryptographically-random bytes yourself and hand them to the constructor.

Below is a drop-in replacement that:

1. Creates a fresh 128-bit AES key (32 hex chars).  
2. Creates a fresh 7-byte tweak (14 hex chars) exactly as required by FF3-1.  
3. Keeps your radix-10 example intact.

```python
import secrets
from ff3 import FF3Cipher

# --- dynamic generation -------------------------------------------------
key   = secrets.token_hex(16)        # 16 bytes → 32 hex chars
tweak = secrets.token_hex(7)         # 7  bytes → 14 hex chars
# ------------------------------------------------------------------------

cipher = FF3Cipher(key, tweak)

plaintext  = "3992520240"
ciphertext = cipher.encrypt(plaintext)
decrypted  = cipher.decrypt(ciphertext)

print("key  :", key)
print("tweak:", tweak)
print(f"{plaintext} -> {ciphertext} -> {decrypted}")
```

Run it a few times and you’ll see new key/tweak values every execution while still producing valid FF3-1 ciphertexts.
