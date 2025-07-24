Below is a “decision tree” plus some concrete implementation notes that have worked for other banks / processors.  It will help you decide whether to (A) outsource the de-tokenization problem to an industry utility such as TCH, or (B) build an in-house service and expose it only to the payment network (banks), while keeping aggregators on tokens.

────────────────────────────────────────
1.  Clarify the actors and trust boundaries
   • You (the API provider / bank) – ultimate owner of the real account number (PAN).  
   • Aggregators – should NEVER see the real PAN; they work only with tokens.  
   • Receiving bank – must see the real PAN to post the credit.  
   • Optional industry utility (e.g. TCH Token Service, Akoya, etc.) – already trusted by most US banks.

2.  Pick a token type
   a. Reversible token (must be de-tokenizable by somebody).  
   b. Format-preserving so that downstream ACH / RTP rails do not break.  
   c. Rotatable / dynamic so the same account produces a different token each time the aggregator asks – defeats look-up tables.  This is supported by both TCH and modern in-house vaults through “single-use” or “bounded-life” tokens.

3.  Decide WHO is allowed to de-tokenize
   Option 1 – Industry utility (TCH/Akoya)
      • TCH already exposes a de-tokenize endpoint only to enrolled banks.  
      • Aggregators never get that privilege.  
      • You simply issue and accept TCH tokens; TCH handles translation when the payment message arrives at the receiving bank.  
      • Pros: zero build, network effects, regulatory acceptance.  
      • Cons: external dependency, small per-token fee.

   Option 2 – In-house de-tokenization service
      • You run a micro-service that maps token → real PAN.  
      • Expose it ONLY inside the payment network’s private MPLS/VPN, or via mutual-TLS white-listed IPs of partner banks.  
      • Aggregators can never reach it.  
      • Make tokens dynamic: issue a new UUID each time the aggregator requests an account reference; store (token, PAN, expiry, aggregator-id, purpose) in an encrypted vault.  After expiry or first use the row is hard-deleted so a static table can’t be built.  
      • Pros: full control, no third-party fee.  
      • Cons: you must run a PCI-DSS-level vault, 24×7 HA, key rotation, monitoring, audits, and convince every receiving bank to call your endpoint (or embed an SDK that calls you).

4.  Implementation checklist (if you choose Option 2)
   • Token format: 18-digit numeric, same length as DDA to keep ACH happy (format-preserving).  
   • Crypto: AES-256 in FPE mode (FF3-1) with an HSM-backed daily key; new key daily so yesterday’s tokens are useless.  
   • Vault: append-only table, row TTL = 7 days or “single-use” flag.  
   • De-tokenize API:  
        POST /detokenize  
        {token, bankId, traceId}  
        returns {pan, routing} only if caller is in bank allow-list.  
   • Security:  
        – mTLS + OAuth2 (client-credential flow) for every bank.  
        – Rate-limit: 10 req/s per bank, alert if >5 % 404 (possible guessing).  
        – All events shipped to SIEM.  
   • Testing: provide sandbox endpoint + mock tokens so receiving banks can integrate without touching prod PANs.

5.  Migration path
   • Phase 1 – Issue both real PAN and token to aggregator, but mark the PAN “deprecated”.  Aggregators cut over in 90 days.  
   • Phase 2 – Stop returning real PAN.  
   • Phase 3 – Flip the switch so your core only accepts tokens from aggregators.

────────────────────────────────────────
Rule of thumb  
If your traffic is < 5 M tokens / month and you already rely on TCH for other clearing services, outsource (Option 1).  If you need tight control, have the scale to amortize vault costs, or operate in a country without a shared token network, build in-house (Option 2) following the checklist above.

At 1 B tokens / month (≈ 400 k per minute on a business day) the TCH model starts to break on two axes: (1) unit economics, and (2) latency / concurrency.  
TCH’s list price is ~ $0.001–$0.002 per detokenize call, so you are looking at $1–$2 M per month in fees, plus you still have to absorb ~ 50–100 ms RTT for every call they make on your behalf.  
With 1 B tokens you also need deterministic sub-10 ms lookup, horizontal scale and zero external dependency on a third-party SLA.  
That almost always pushes the decision to **build and operate an in-house vault**, but with a few twists that differ from the generic checklist I gave earlier.

────────────────────────────────────────
1.  Architectural sketch tuned for 1 B / mo
   • Token format  
     – 18-digit numeric, Luhn-valid, first 6 digits = pseudo-BIN reserved for your token range.  
     – 128-bit encrypted payload (AES-256-GCM) encoded into the last 12 digits using a radix-10 alphabet.  The payload contains (real PAN + 32-bit counter + 40-bit expiry epoch + 24-bit reserved).  
     – Key rotation every 24 h; yesterday’s ciphertext is unreadable even if stolen, so tokens are dynamic by construction.

   • Vault micro-service  
     – Stateless edge pods that only do encryption/decryption; no persistence.  
     – All state lives in a sharded, in-memory KV store (e.g. Aerospike / Redis-Cluster) with 3× replication per AZ.  
     – Sizing: 1 B tokens × 16 bytes = 16 GB raw data; with 3× replication + indexes ≈ 100 GB RAM across the cluster – trivial on modern 256 GB boxes.  
     – Each token row TTL = 7 days; a nightly Spark job purges expired rows to keep RAM bounded.

   • De-tokenize path  
     – gRPC unary call over mutual-TLS; 99th percentile < 5 ms inside your DC, < 15 ms to partner bank POP.  
     – Rate-limits: 100 k rps aggregate (≈ 2.5× peak), enforced by Envoy sidecar.  
     – Circuit breaker: if >2 % errors, fail closed; banks fall back to exception handling (rare).

   • Security controls  
     – HSM cluster (FIPS 140-3) for key encryption keys (KEKs); data keys in memory only, rotated every hour.  
     – All de-tokenize events streamed to Kafka → SIEM; ML model flags abnormal token reuse.  
     – Quarterly external PCI-DSS audit + SOC-2 Type II.

2.  Roll-out to receiving banks
   • Provide a tiny Java/.NET SDK that wraps the gRPC client plus automatic retry and key pinning.  
   • Offer a sandbox cluster (synthetic PANs) so banks can certify in a week.  
   • SLAs: 99.99 % availability, 50 ms global P99; publish real-time status page.

3.  Economics
   • CapEx: ~ $150 k for HSMs + $100 k for stateless compute (10 c5.4xlarge equiv).  
   • OpEx: $25 k/mo cloud infra + 2 FTE SRE; total < $50 k/mo – two orders of magnitude cheaper than TCH at 1 B tokens.

4.  Migration timeline
   Month 0–1   Build MVP vault + SDK  
   Month 2–3   Certify top 20 receiving banks in parallel  
   Month 4     Shadow traffic (dual-write)  
   Month 5     Cut aggregators to tokens only  
   Month 6     Decommission real-PAN pipeline

Bottom line  
At 1 B tokens/month the cost, latency and control arguments strongly favor an in-house, horizontally scalable, HSM-backed de-tokenization service exposed only to the payment network.

With 1B requests per month, you're dealing with significant scale that requires careful architectural planning. Let me address the high-volume considerations:

## Scale Requirements
- **~400 requests/second** average
- **Peak traffic**: Likely 1,000-2,000 RPS during business hours
- **99.99%+ uptime** required for financial services
- **Sub-100ms response times** for good user experience

## High-Scale Architecture Design

### 1. **Distributed Tokenization Service**

```yaml
Load Balancer → [API Gateway] 
               → [Token Service Cluster - 10-20 nodes]
               → [Cache Layer - Redis Cluster]
               → [Database - Sharded PostgreSQL/Cassandra]
               → [HSM Cluster for key management]
```

### 2. **Caching Strategy** (Critical for performance)
- **L1 Cache**: In-memory (local to each service instance)
- **L2 Cache**: Redis cluster with ~10-20 nodes
- **Cache hit target**: 95%+
- **TTL strategy**: Dynamic based on token usage patterns

### 3. **Database Sharding**
```sql
-- Shard by token prefix or bank_id
Shard 1: Tokens starting with 0-2
Shard 2: Tokens starting with 3-5
Shard 3: Tokens starting with 6-8
Shard 4: Tokens starting with 9-A
...
```

### 4. **Performance Optimizations**

**Token Structure for Fast Lookup:**
```
TOK-[BANK_ID]-[TIMESTAMP]-[RANDOM_STRING]-[CHECKSUM]
```

**Database Indexing:**
- Primary key on token_id
- Secondary index on bank_id + expiration_time
- Partition pruning by time ranges

## Infrastructure Requirements

### Compute
- **Token Service**: 20-30 c5.xlarge instances (4 vCPU, 8GB RAM)
- **Auto-scaling**: Based on CPU utilization and response times
- **Geographic distribution**: Multiple regions for latency

### Storage
- **Primary DB**: Sharded PostgreSQL with read replicas
- **Cache**: Redis cluster (10-15 nodes, 30-50GB each)
- **Cold storage**: Archive old tokens to cheaper storage

### Network
- **Bandwidth**: Plan for 10-20 Gbps peak
- **CDN**: For static content if needed
- **Private networking**: Between services where possible

## High Availability Design

### Multi-Region Setup
```
Primary Region (us-east-1)
├── Active token service
├── Primary database
└── Full cache cluster

Secondary Region (us-west-2)
├── Standby token service
├── Read-only database replica
└── Warm cache cluster
```

### Failure Scenarios Handling
1. **Single node failure**: Auto-healing within 30 seconds
2. **Regional outage**: Failover in 2-5 minutes
3. **Cache failure**: Graceful degradation to database
4. **Database issues**: Circuit breaker patterns

## Monitoring & Observability

### Key Metrics to Track
- **Request rate**: By endpoint, by bank
- **Latency**: p50, p95, p99, p99.9
- **Error rates**: By type, by bank
- **Cache hit ratios**: Overall and by token type
- **Database performance**: Query times, connection pool

### Alerting Thresholds
- **Latency**: >100ms for 5 consecutive minutes
- **Error rate**: >0.1% for any 5-minute window
- **System health**: Any component >85% utilization

## Cost Considerations

### Infrastructure Costs (Monthly)
- **Compute**: $15,000-25,000
- **Storage**: $5,000-10,000
- **Networking**: $3,000-5,000
- **HSM/Security**: $2,000-5,000
- **Total**: ~$25,000-45,000/month

### Optimization Strategies
1. **Request batching** where possible
2. **Efficient serialization** (protobuf vs JSON)
3. **Connection pooling** everywhere
4. **Asynchronous processing** for non-critical operations

## Data Management at Scale

### Token Lifecycle Management
```python
# Automated cleanup jobs
- Expired token deletion: Every 15 minutes
- Cold data archiving: Daily
- Analytics aggregation: Hourly
```

### Backup Strategy
- **Hot backup**: Every 15 minutes
- **Point-in-time recovery**: Enabled
- **Cross-region replication**: Automatic

## Implementation Phases

### Phase 1: MVP (3-4 months)
- Basic tokenization/detokenization
- Single region, moderate scaling
- Essential monitoring

### Phase 2: Scale & HA (2-3 months)
- Multi-region deployment
- Full caching layer
- Advanced monitoring

### Phase 3: Optimization (Ongoing)
- Performance tuning
- Cost optimization
- Advanced features

## Critical Success Factors

1. **Start with realistic load testing** - simulate 2x expected traffic
2. **Implement circuit breakers** early
3. **Design for graceful degradation**
4. **Plan your deployment strategy** - blue-green deployments
5. **Security-first approach** - compliance requirements will be strict

Would you like me to dive deeper into any specific aspect of the high-scale implementation?

Thank you for the clarification. Below is a more **complete architectural evaluation** write-up, framed for a **Confluence page**. It covers the overall design decision — not just the technical mechanics of tokenization, but also the strategic question of **whether to use an external provider (like TCH), build in-house, or explore a hybrid or alternative model**.

---

# Tokenized Account Number Infrastructure: Design Evaluation and Recommendation

## Purpose

This document evaluates architectural options for implementing a **tokenized account number system** within a multi-party payment ecosystem. The goal is to protect sensitive account numbers from exposure while ensuring that payments can flow securely and efficiently between aggregators, banks, and end systems. The document compares using a third-party provider (e.g. The Clearing House, or TCH) versus building and managing our own tokenization infrastructure, and explores other possible alternatives.

---

## Background

In our ecosystem:

* We are an **API provider** offering payment APIs to **aggregators**.
* Aggregators, in turn, interface with **end-users** and initiate **payments**.
* To protect sensitive account information, we wish to **tokenize account numbers** before exposing them to aggregators.
* However, **banks must still be able to process and resolve the actual account numbers** when executing payments, which implies controlled **de-tokenization** capability.

---

## Requirements

The system must support the following:

| Requirement                            | Description                                                                                                           |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Account Protection**                 | Aggregators must not have access to raw account numbers.                                                              |
| **De-tokenization Capability**         | Banks must be able to obtain the actual account numbers when executing payments.                                      |
| **Token Irreversibility (externally)** | Tokens should not be guessable or easily mapped back to account numbers by aggregators or other unauthorized parties. |
| **Controlled De-tokenization Access**  | Only authorized banks and systems should be allowed to de-tokenize tokens.                                            |
| **Statelessness (preferred)**          | Avoiding a token-to-account mapping database is desirable for scalability and manageability.                          |
| **Token Dynamism**                     | Prevent long-term token reuse to reduce correlation and replay risks.                                                 |
| **Operational Simplicity**             | Minimize dependencies, integration overhead, and security surface area.                                               |

---

## Design Options

### Option 1: Use a Centralized Tokenization Service (e.g., TCH)

The Clearing House (TCH) and similar providers offer a **centralized tokenization and de-tokenization infrastructure** that is already trusted by many banks.

#### Advantages

* Industry-standard and already integrated with many financial institutions.
* Simplifies token resolution by allowing banks to interact directly with TCH for de-tokenization.
* Mature access control, governance, and security processes.
* Reduces need for us to manage sensitive de-tokenization logic.

#### Disadvantages

* **External dependency**: Integration timelines are dependent on third-party coordination.
* **Limited control** over customization, formats, and dynamic behavior.
* **Aggregators cannot directly de-tokenize** (which is desirable), but operational coordination is required between aggregator, our platform, and TCH.
* Integration complexity and onboarding friction for each participant.
* Reliant on TCH’s SLA, support timelines, and pricing structure.

#### Use Case Fit

Best suited for organizations already deeply embedded in financial infrastructure ecosystems, or those who want to minimize compliance and audit burden by offloading token governance.

---

### Option 2: Build Our Own Tokenization and De-tokenization Infrastructure

In this approach, we build and host both the **token generation logic** and the **de-tokenization API**, which is securely exposed **only to trusted banks**.

#### Token Design Considerations

* Use **Format-Preserving Encryption (FPE)** to allow stateless, reversible tokenization.
* Include **contextual tweaks** (e.g., aggregator ID, timestamp) to make tokens dynamic and context-bound.
* Expose a **secure de-tokenization service** to banks, protected via mTLS, client authentication, IP allowlisting, and rate-limiting.

#### Advantages

* Full control over token format, expiry, lifecycle, and encryption logic.
* Enables fast customization and integration with aggregators and banking partners.
* No dependency on external services or registries.
* Easier to align with internal data protection and security policies.

#### Disadvantages

* We must manage:

  * Secure key infrastructure (e.g., HSM/KMS).
  * Token format compatibility.
  * Regulatory and audit implications.
* Need to maintain high availability and compliance of the de-tokenization API.
* Requires coordination with banks for consuming our de-tokenization API securely.

#### Use Case Fit

Ideal for platforms looking for **flexibility**, **lower operational dependency**, and **ownership of the tokenization pipeline**, particularly in API-driven ecosystems.

---

### Option 3: Hybrid Approach (Federated or Delegated De-tokenization)

A potential third approach involves **delegating de-tokenization responsibility to banks** without building a full external token registry like TCH.

For example:

* We generate **encrypted token envelopes** using public-key encryption or symmetric authenticated encryption (e.g., AES-GCM).
* Each envelope is **bound to a specific recipient bank**, such that only that bank can decrypt the token using a pre-shared key or certificate.
* Aggregators pass this token as-is.
* The bank can decrypt and access the original account number without calling an external service.

#### Advantages

* Fully stateless and secure.
* Removes the need for a central de-tokenization service.
* High performance and minimal latency.
* Fine-grained control over token usage policies.

#### Disadvantages

* Requires distribution and management of encryption keys or certificates to every receiving bank.
* Operational overhead in managing bank-specific encryption setups.
* Difficult to revoke tokens or enforce fine-grained expiration after issuance.

#### Use Case Fit

Useful in closed-loop or partner-controlled environments where bank participants can agree on encryption and key-sharing models.

---

## Comparative Summary

| Criterion                   | TCH (External Provider)  | Build In-house     | Hybrid Envelope |
| --------------------------- | ------------------------ | ------------------ | --------------- |
| Integration Complexity      | High                     | Medium             | High            |
| Control and Flexibility     | Low                      | High               | High            |
| Token Format Customization  | Limited                  | Full               | Full            |
| Stateless Operation         | Yes                      | Yes (if using FPE) | Yes             |
| Third-party Dependency      | High                     | None               | None            |
| Revocation / Expiry Control | Moderate                 | Full               | Limited         |
| Ease of Bank Adoption       | High (if TCH-integrated) | Medium             | Low             |
| Aggregator Isolation        | Yes                      | Yes                | Yes             |

---

## Recommendation

Based on our requirements, operational preferences, and integration capabilities, the recommended approach is:

### **Build Our Own Tokenization and De-tokenization Infrastructure**

This approach provides the best balance of:

* Control over token format and context-binding,
* Stateless and secure operation using industry-standard cryptographic methods (e.g., FPE),
* Selective exposure of de-tokenization capability to banks only,
* Avoidance of third-party dependencies and integration timelines.

While there is additional implementation and security overhead, these are offset by the architectural flexibility and lower operational risk in the long term. Further, this approach gives us the ability to fine-tune token behavior and support custom requirements from both aggregators and financial institutions.

---

## Next Steps

1. **Finalize cryptographic design** (e.g., AES-FF1 with aggregator-bound tweaks).
2. **Define and implement a secure de-tokenization API** (e.g., REST over mTLS).
3. **Onboard partner banks** with appropriate access and authentication controls.
4. **Define fallback or interop mechanism** in case future TCH integration is needed.

---

Let me know if you'd like this written in Confluence markup format or exported as Markdown, PDF, or another medium.


────────────────────────────────────────  
PART A – FULL ECOSYSTEM ARCHITECTURE  
────────────────────────────────────────  

1. Actors & Trust Boundaries  
   • Your Bank / Core API provider – owns the real DDA/ACH account numbers.  
   • Aggregators – build UI/UX for end-users; **must never see real PANs**.  
   • End-Users – interact only with aggregator apps.  
   • Receiving Banks – must receive the real PAN to post the credit.  
   • Payment Rails – ACH, RTP, FedNow, etc. (require 18-digit numeric identifiers).  
   • Optional Token Vault Operator – either you or a shared utility (TCH, Akoya, etc.).  

2. Data Flow (happy path)  
   1. End-user enters real account number → Aggregator **POST /link-account** to you.  
   2. **Tokenize**: Your API returns an 18-digit token T.  
   3. Aggregator stores T and uses it for every future payment instruction.  
   4. When aggregator calls **POST /initiate-payment** they send T + amount + beneficiary bank.  
   5. Your backend swaps T → real PAN, attaches the real PAN to the payment message, and injects it into the payment rail.  
   6. Receiving bank sees the real PAN and posts the credit.  

3. Security & Control Layers  
   • Channel: mTLS + OAuth2 client-credential flow between every pair of actors.  
   • Vault: isolated subnet, HSM-backed keys, no direct aggregator access.  
   • Audit: every tokenization / detokenization event streamed to SIEM; 90-day retention.  
   • Compliance: PCI-DSS L1, SOC-2 Type II, annual FedLine penetration test.  

4. Deployment Patterns  
   • Multi-AZ active-active clusters (stateless crypto pods + stateful KV shards).  
   • Global Anycast DNS to edge POPs for < 10 ms latency to banks.  
   • Disaster Recovery: cross-region async replication with RPO < 5 min.  

────────────────────────────────────────  
PART B – TOKENIZATION METHOD CHOICE  
────────────────────────────────────────  

Decision Matrix (1 B tokens / month)

| Criterion                     | In-house FPE Vault             | TCH / Shared Utility           |
|------------------------------|--------------------------------|--------------------------------|
| **Unit cost**                | ~ $0.00005 / token             | ~ $0.001–$0.002 / token        |
| **Latency**                  | 5–10 ms intra-DC               | 50–100 ms + Internet RTT       |
| **Control / Road-map**       | Full                           | External roadmap               |
| **Regulatory burden**        | You run PCI audits             | Shared audits (lighter)        |
| **Migration effort**         | Convince every bank to call you| Banks already integrated       |
| **Static-token risk**        | Daily key rotation defeats     | Also supports dynamic tokens   |
| **Format compliance**        | 18-digit numeric               | 18-digit numeric               |

Conclusion  
At 1 B tokens / month the cost delta alone (~ $1 M+/yr vs ~ $50 k/yr) plus the need for sub-10 ms deterministic latency make **in-house, HSM-backed, format-preserving tokenization** the clear winner.  The ecosystem design in Part A already assumes this choice; if you later decide to outsource, only the vault boundary and SLA sections change—the rest of the ecosystem diagram stays identical.
