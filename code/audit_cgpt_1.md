The proposed solution is a centralized audit logging system designed to ingest audit events from multiple microservices (e.g., login, consent, payments) through Kafka and store them in a tamper-evident and queryable format in MongoDB. Each service posts structured audit events to a Kafka topic, which are then consumed by a Kafka consumer that validates, enriches, and inserts them into MongoDB. The events include rich context, such as customer, third party, or aggregator identifiers, along with metadata like timestamps, event types, and action details. MongoDB collections are indexed for fast queries and configured with TTL (time-to-live) indexing to automatically expire records after three years, ensuring compliance with data retention policies while keeping storage costs low.

To ensure data integrity and tamper-evidence, the system uses a hash chaining mechanism—each audit record includes a cryptographic hash of its contents combined with the hash of the previous record. To avoid contention under high write volumes, hash chains are scoped per logical partition (e.g., per source app per day), and latest hashes are tracked in-memory or in a fast store like Redis. This maintains verifiability while supporting high throughput. A console UI enables support and compliance users to search audit logs, trace user activity, and verify event integrity. Optional cold archiving (e.g., to S3) of older data enables further cost optimization without sacrificing long-term accessibility.

Capture audit events from multiple services (login, consent, payments, etc.)

Maintain rich context (customer, third party, aggregator)

Ensure data immutability and tamper resistance

Retain data for 3 years and purge automatically

Provide query interface for support, compliance, and investigation teams

Be cost-effective and scalable for write-heavy workloads

Here is a **comprehensive audit event schema** designed to fulfill the requirements of regulation **§1033.351** as well as typical metadata needed for observability, traceability, and tamper detection.

---

## ✅ Full Audit Event Schema

```json
{
  "eventId": "evt_001",                          // Unique identifier
  "eventType": "access_denial",                  // Enum: access_request, access_denial, information_request, information_denial, authorization_provided, authorization_revoked, performance_record, policy_updated, disclosure_provided
  "timestamp": "2025-04-30T10:45:00Z",           // ISO 8601 timestamp
  "sourceApp": "consent-management",             // System where event originated
  "retentionCategory": "reg_1033.351_d1ii",      // For determining TTL (3 years, etc.)
  "retentionExpiry": "2028-04-30T10:45:00Z",     // Optional: Explicit timestamp for deletion
  "interfaceType": "developer",                  // developer | consumer | internal

  // Contextual Identity
  "consumerId": "cus_123",                       // End user
  "thirdPartyId": "tp_456",                      // TPP making request
  "aggregatorId": "agg_789",                     // Optional: If applicable
  "userAgent": "Mozilla/5.0",                    // Metadata: user agent
  "ipAddress": "203.0.113.10",                   // Metadata: IP address
  "geoLocation": "37.7749,-122.4194",            // Optional

  // Request/Response Context
  "requestId": "req_001",                        // Correlates request/response
  "responseContextId": "ctx_001",                // To group request-denial pairs
  "status": "denied",                            // success | denied | pending
  "denialReasonCode": "NO_AUTH",                // Short code
  "denialReasonDescription": "No valid auth",    // Human-readable reason
  "communicationMethod": "API",                  // API | email | portal

  // Authorization / Revocation Specific
  "authorizationMethod": "OAuth2.0",             // If applicable
  "revocationMethod": "Consumer UI",             // If applicable
  "effectiveTimestamp": "2025-04-29T08:00:00Z",  // When authorization/revocation took effect

  // Data Visibility / Field Tracking
  "dataFieldsRequested": ["account.balance", "account.transactions"],
  "dataFieldsDenied": ["account.transactions"],
  "reasonForOmission": "§1033.221(b)(2)",        // Reference to regulation
  "standardConformance": "FAPI-RW-1.0",          // Consensus standard followed (optional)

  // Performance Event
  "performanceType": "uptime",                   // Optional: for performance_record
  "performanceValue": "99.98%",
  "performanceWindow": "2025-04",

  // Policy or Disclosure Tracking
  "policyVersion": "v3.2",                       // Optional: for policy_updated
  "policyUpdateDescription": "Added logging of denied access",
  "disclosureType": "terms_of_service",          // Optional
  "disclosureVersion": "2025-03"

  // Audit Metadata
  "createdBy": "system",                         // Who created this audit record
  "createdAt": "2025-04-30T10:45:01Z",           // Insertion time
  "ingestionMethod": "kafka-consumer-v1",        // How it was ingested
  "processingRegion": "us-west-2",               // Optional: for geo partitioning

  // Tamper Proofing
  "hash": "f7a2c4b...e9b12d",                    // Hash of this record
  "prevHash": "c3b1a1e...bd7c45",                // Hash chain
  "chainPosition": 982343                        // Optional: sequence number
}
```

---

## 🧾 Notes

* Fields like `eventType`, `retentionCategory`, and `denialReasonCode` should ideally be enumerated to ensure consistency.
* The `prevHash` + `hash` fields establish a **hash chain** for tamper detection. This assumes **records are strictly ordered** by some logic (e.g., partition key).
* `createdAt` and `timestamp` may differ slightly if ingestion delays occur.
* The `retentionExpiry` field can help TTL indexing or batch cleanups.
* If using MongoDB, **sparse or optional fields** like `performanceType`, `authorizationMethod`, etc., can remain absent unless relevant.

---

Would you like this schema in JSON Schema format with type validation included?
