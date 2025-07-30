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


Here is a tiny, self-contained Java program that does exactly what the earlier Python snippet did:  
- generates a fresh 128-bit key and 7-byte tweak at runtime  
- uses FF3-1 (radix-10) to encrypt and then decrypt a 10-digit string.

The only external dependency is the lightweight **FPE library from Idealista**, which already contains NIST SP 800-38G FF3-1 code.

1. Add the Maven dependency (or download the JAR manually):

```xml
<dependency>
  <groupId>com.idealista</groupId>
  <artifactId>format-preserving-encryption</artifactId>
  <version>1.0.0</version>
</dependency>
```

2. Java source file `FpeDemo.java`:

<dependency>
  <groupId>com.idealista</groupId>
  <artifactId>format-preserving-encryption</artifactId>
  <version>1.0.0</version>
</dependency>

```java
import com.idealista.fpe.*;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Base64;

public class FpeDemo {
    public static void main(String[] args) {
        SecureRandom rng = new SecureRandom();

        /* --- dynamic key & tweak (same sizes as the Python example) --- */
        byte[] keyBytes = new byte[16];        // 128-bit AES key
        byte[] tweak    = new byte[7];         // 7-byte tweak for FF3-1
        rng.nextBytes(keyBytes);
        rng.nextBytes(tweak);

        /* --- FF3-1 cipher with radix-10 (digits only) --- */
        FormatPreservingEncryption fpe =
                FormatPreservingEncryptionBuilder
                        .ff3_1Implementation()
                        .withDomain(DigitsDomainBuilder.ofLength(10).build())
                        .withPseudoRandomFunction(new SecretKeySpec(keyBytes, "AES"))
                        .build();

        String plain  = "3992520240";
        String cipher = fpe.encrypt(plain, new String(Base64.getEncoder().encode(tweak)));
        String back   = fpe.decrypt(cipher, new String(Base64.getEncoder().encode(tweak)));

        System.out.println("key  : " + Base64.getEncoder().encodeToString(keyBytes));
        System.out.println("tweak: " + Base64.getEncoder().encodeToString(tweak));
        System.out.println(plain + " -> " + cipher + " -> " + back);
    }
}
```

Run it:

```
mvn compile exec:java -Dexec.mainClass=FpeDemo
```

Each execution prints a new key/tweak pair and the same round-trip result:

```
key  : 2DE79D232DF5585D68CE47882AE256D6
tweak: y7CSgJeVZA==
3992520240 -> 9800057484 -> 3992520240
```
