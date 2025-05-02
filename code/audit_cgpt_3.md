Here is the **MongoDB `createCollection` command** along with the **recommended indexes** to support efficient querying, compliance with retention, and tamper-proofing using a hash chain.

---

### ✅ `createCollection` with JSON Schema Validation

```js
db.createCollection("audit_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["eventId", "eventType", "timestamp", "sourceApp", "createdAt", "hash"],
      properties: {
        eventId: { bsonType: "string" },
        eventType: { bsonType: "string" },
        timestamp: { bsonType: "date" },
        sourceApp: { bsonType: "string" },
        retentionCategory: { bsonType: "string" },
        retentionExpiry: { bsonType: "date" },
        consumerId: { bsonType: "string" },
        thirdPartyId: { bsonType: "string" },
        aggregatorId: { bsonType: "string" },
        status: { bsonType: "string" },
        denialReasonCode: { bsonType: "string" },
        createdBy: { bsonType: "string" },
        createdAt: { bsonType: "date" },
        hash: { bsonType: "string" },
        prevHash: { bsonType: "string" },
        chainPosition: { bsonType: "int" }
      }
    }
  }
});
```

---

### 🧠 Index Strategy

To support retention, querying, and tamper detection, use these indexes:

#### 1. **TTL Index** (for auto-deletion after 3 years)

```js
db.audit_events.createIndex({ retentionExpiry: 1 }, { expireAfterSeconds: 0 });
```

> ⚠️ Make sure `retentionExpiry` is set at insert time for this to work.

---

#### 2. **Hash Chain Verification**

```js
db.audit_events.createIndex({ hash: 1 }, { unique: true });
db.audit_events.createIndex({ prevHash: 1 });
```

> Useful if you need to verify the chain or detect tampering.

---

#### 3. **Query Indexes for Investigations**

```js
db.audit_events.createIndex({ consumerId: 1, timestamp: -1 });
db.audit_events.createIndex({ thirdPartyId: 1, timestamp: -1 });
db.audit_events.createIndex({ sourceApp: 1, timestamp: -1 });
```

---

#### 4. **Event Type and Status Indexing**

```js
db.audit_events.createIndex({ eventType: 1, status: 1, timestamp: -1 });
```

---

#### 5. **Full-Text Search Index** (Optional)

```js
db.audit_events.createIndex({ denialReasonDescription: "text", policyUpdateDescription: "text" });
```

---

Would you like me to generate the Mongo shell commands or the equivalent Mongoose schema in Node.js?
