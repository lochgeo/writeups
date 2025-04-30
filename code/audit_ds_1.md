# Audit Record System Design

## Overview
Your approach to use Kafka as an event bus and MongoDB for storage is sound. Let me break down the key components and considerations for your audit system.

## Architecture Components

### 1. Event Producers (Client Applications)
- Login app, consent management, payments, accounts, etc.
- Each should publish standardized audit events to Kafka

### 2. Kafka Topics
- Consider separate topics for different event types/priorities
- Recommended topic structure:
  - `audit.events.high` (critical security events)
  - `audit.events.medium` (important business events)
  - `audit.events.low` (informational events)

### 3. Consumer Service
- Processes Kafka messages and stores in MongoDB
- Should include validation and transformation logic
- Consider idempotent processing to handle duplicates

### 4. MongoDB Storage
- Schema design is critical for query performance
- Recommended collection structure with time-based partitioning

## Data Model Considerations

### Essential Fields to Capture:
```javascript
{
  eventId: UUID,                  // Unique event identifier
  timestamp: ISODate,              // When event occurred
  eventType: String,               // e.g., "login", "payment", "consent_change"
  eventStatus: String,            // "success", "failed", "rejected"
  sourceSystem: String,           // Originating application
  
  // Actor context (can be any of these)
  customerId: String,             // Optional
  thirdPartyId: String,           // Optional
  aggregatorId: String,           // Optional
  serviceAccountId: String,       // Optional
  
  // Relationship between actors
  actingOnBehalfOf: String,       // When third party acts for customer
  delegatedThrough: String,       // When using aggregator
  
  ipAddress: String,              // Source IP
  userAgent: String,              // Client info
  deviceId: String,               // Optional
  
  // Event-specific details
  action: String,                 // What happened
  targetResource: String,         // What was affected
  beforeState: Object,            // Optional - state before change
  afterState: Object,             // Optional - state after change
  reason: String,                 // Why rejected/failed
  
  // Tamper-proofing
  hashChain: String,              // For integrity verification
  previousHash: String            // Links to previous record
}
```

## Tamper-Proofing Implementation

### Hash Chain Approach:
1. For each new record:
   - Take the previous record's hash (or system seed for first record)
   - Concatenate with current record's immutable fields (eventId, timestamp, etc.)
   - Generate SHA-256 hash of this concatenation
   - Store as `hashChain` in current record

2. Verification Process:
   - Recompute hashes sequentially
   - Compare with stored hashes to detect any tampering

## Retention Management

### MongoDB TTL Index:
```javascript
// Automatically delete documents after 3 years
db.auditRecords.createIndex(
  { "timestamp": 1 },
  { expireAfterSeconds: 94608000 } // 3 years in seconds
);
```

### Archive Strategy:
- Consider moving older data to a separate archive collection
- Or compress and move to cold storage (S3, etc.)

## Query Interface

### Console View Options:
1. **Direct MongoDB Access** (for technical users):
   - Build indexes on common query fields (customerId, timestamp, eventType)
   
2. **API Layer** (for business users):
   - REST/GraphQL API with endpoints like:
     - `/audit/customer/{id}?from=DATE&to=DATE`
     - `/audit/search?type=LOGIN&status=REJECTED`

3. **UI Dashboard**:
   - Filters for customer, date range, event type, status
   - Export capabilities for compliance reporting

## Implementation Recommendations

1. **Schema Validation**:
   - Enforce schema at Kafka producer level (Avro schemas)
   - Validate again in consumer before MongoDB insert

2. **Error Handling**:
   - Dead letter queue for failed messages
   - Monitoring for processing delays

3. **Performance**:
   - Indexes on: customerId, timestamp, eventType, status
   - Consider time-based collections (e.g., `audit_2023`, `audit_2024`)

4. **Security**:
   - Encrypt sensitive fields at application level
   - Implement proper access controls for the console

Would you like me to elaborate on any specific aspect of this design?
