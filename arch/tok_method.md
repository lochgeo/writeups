Certainly. Here's a formal, comprehensive write-up suitable for a Confluence page:

---

# Tokenization Design for Secure Account Number Handling

## Overview

This document outlines the design considerations and technical approaches for tokenizing account numbers in a payment processing ecosystem involving API providers, aggregators, and banks. The objective is to protect sensitive account information while maintaining the ability to process payments end-to-end, including cross-bank transactions, without exposing raw account numbers to intermediaries.

---

## Problem Statement

As an API provider, we are integrating with aggregators who deliver services to end-users. When aggregators initiate payments, they pass along account numbers that may be visible within their systems or inadvertently exposed. To mitigate this, we aim to tokenize account numbers such that:

* Aggregators only receive tokenized account numbers.
* Only authorized banks can de-tokenize the tokens back to the original account numbers.
* Tokens must be dynamic or context-bound to prevent reverse engineering or token mapping.
* De-tokenization must be possible in downstream systems (e.g., the recipient bank) without relying on external token registries unless explicitly chosen.
* Ideally, the system should avoid maintaining a central database of token mappings to reduce complexity and improve scalability.

---

## Key Requirements

| Requirement                | Description                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Tokenization               | Real account numbers must not be visible to aggregators.                                                           |
| Controlled De-tokenization | Only banks should be able to de-tokenize tokens via a secure service.                                              |
| Stateless Operation        | Minimize or eliminate the need for persistent token mapping databases.                                             |
| Anti-Reverse Engineering   | Tokens should not be easily guessable or reproducible by unauthorized actors.                                      |
| Dynamic Tokens             | Tokens should be context-bound (e.g., per session or aggregator) to reduce the risk of long-term reuse or mapping. |

---

## Evaluation of Approaches

### 1. Hashids

**Hashids** is a library that encodes integers into obfuscated strings and supports deterministic decoding.

* **Advantages**:

  * Stateless and reversible.
  * Easy to implement.

* **Disadvantages**:

  * Not cryptographically secure.
  * Vulnerable to brute-force and reverse-engineering, especially when input ranges (e.g., account numbers) are predictable or short.
  * Unsuitable for protecting sensitive financial data.

**Conclusion**: Not suitable for secure account number tokenization in this context.

---

### 2. Format-Preserving Encryption (FPE)

**Format-Preserving Encryption** (e.g., AES-FF1 or FF3 under NIST SP 800-38G) encrypts data while preserving its format.

* **Advantages**:

  * Reversible and deterministic encryption.
  * Output resembles the original account number format, facilitating system compatibility.
  * Stateless operation: does not require token mapping storage.
  * Supports dynamic tokens through tweakable parameters (e.g., aggregator ID, timestamp).

* **Disadvantages**:

  * Requires secure key management (e.g., via HSMs).
  * More complex to implement than simple hash-based solutions.

**Conclusion**: Strong candidate for secure, stateless, reversible tokenization.

---

### 3. HMAC-based Tokens with Context Binding

Using an HMAC with a secret key and additional contextual information (e.g., aggregator ID, timestamp):

```plaintext
token = HMAC(master_key, account_number || aggregator_id || nonce)
```

* **Advantages**:

  * Cryptographically secure.
  * Context-specific tokens reduce reuse and improve traceability.

* **Disadvantages**:

  * Not reversible without either:

    * Rechecking against a list of known account numbers (inefficient), or
    * Maintaining a token mapping database (adds state).
  * Not suitable for large-scale stateless de-tokenization.

**Conclusion**: Suitable for short-lived or one-time-use tokens but not ideal for reversible, stateless systems.

---

### 4. Encrypted Token Envelopes

Tokens can be created by encrypting the account number and associated metadata (e.g., timestamp, aggregator ID) and base64-encoding the result:

```plaintext
token = base64(AES_encrypt(account_number, key, iv=random))
```

* **Advantages**:

  * Secure and reversible.
  * Allows expiration and metadata binding.
  * Can be implemented in a JWT- or JWE-like structure.

* **Disadvantages**:

  * Requires banks to integrate with a de-tokenization service or manage decryption keys securely.
  * Larger token size due to encryption overhead.

**Conclusion**: Suitable for systems where de-tokenization can be delegated to a secure internal service.

---

### 5. Token Mapping Database (Traditional Tokenization)

Tokens are generated randomly and stored alongside the real account number in a secure database.

* **Advantages**:

  * Flexible and simple to implement.
  * Supports expiration, revocation, and auditability.

* **Disadvantages**:

  * Requires token persistence and secure database management.
  * Stateful, potentially less scalable.

**Conclusion**: Useful in low-scale or high-control environments but less desirable for stateless architectures.

---

## Recommended Architecture

Based on the above evaluations, the following architecture is recommended:

### Tokenization Engine

* Use **AES-FF1 format-preserving encryption** with a tweak parameter that includes the aggregator ID and optionally a timestamp.
* The encryption key must be stored securely (e.g., HSM or KMS).
* Each aggregator receives a unique token per account, reducing the risk of token correlation.

### De-tokenization Service

* Expose a secure **de-tokenization API** to authorized banks only.
* Authenticate and authorize access using mTLS, API keys, client certificates, and IP allowlisting.
* Maintain audit logs and enforce rate limiting.
* Optionally implement an internal caching layer to support high-throughput lookups.

### Token Lifecycle Management

* Allow token expiration based on configurable time windows or usage policies.
* Bind tokens to aggregators or specific transaction sessions.
* Detect and block reuse of expired or invalid tokens.

---

## Security Considerations

* **Key Management**: Store cryptographic keys securely using HSM or cloud-based KMS with strict access control.
* **Access Control**: Only banks should be able to call the de-tokenization API. Aggregators should never receive decrypted account numbers.
* **Tamper Prevention**: All tokens must be integrity-protected using authenticated encryption (e.g., AES-GCM or AES-SIV).
* **Monitoring**: Implement anomaly detection on token usage patterns and API access.
* **Auditing**: Maintain detailed logs for all tokenization and de-tokenization operations.

---

## Conclusion

To satisfy the design objectives of tokenizing account numbers for use in a multi-party payment ecosystem while avoiding persistent token storage, **Format-Preserving Encryption (FPE)** is the recommended approach. It provides a balance of security, reversibility, and statelessness. A secure de-tokenization service should be built to allow banks to retrieve the original account numbers as needed, under strict access control.

Alternate methods such as HMAC-based tokens, encrypted envelopes, or mapping databases may be used depending on specific use cases, but each has trade-offs in terms of security, scalability, or operational complexity.

---

Let me know if you'd like this exported as Markdown, HTML, or added to an actual Confluence-compatible format.
