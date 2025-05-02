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


Absolutely! Here's a **capacity sizing estimate** for your MongoDB audit log system under two traffic scenarios: **1,000** and **10,000** events per day.

---

## 📦 Assumptions for Sizing

| Parameter            | Value                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| **Document size**    | \~1 KB (typical for audit logs with hashes, IDs, timestamps, and optional metadata)            |
| **Retention period** | 3 years (\~1,095 days)                                                                         |
| **Replication**      | Replica set with 3 nodes (primary + 2 secondaries)                                             |
| **Storage overhead** | 20% overhead for indexes and BSON padding                                                      |
| **Compression**      | WiredTiger with snappy compression (\~50% savings, but not included in worst-case calculation) |

---

## 📊 Sizing Calculations

### 📈 Daily Write Volume

| Traffic | Events/day | Event Size | Daily Volume |
| ------- | ---------- | ---------- | ------------ |
| Low     | 1,000      | 1 KB       | 1 MB/day     |
| High    | 10,000     | 1 KB       | 10 MB/day    |

---

### 🗓️ 3-Year Raw Data Storage (Before Replication and Overhead)

| Traffic    | Days  | Total Events | Raw Size |
| ---------- | ----- | ------------ | -------- |
| 1,000/day  | 1,095 | 1.1 million  | \~1.1 GB |
| 10,000/day | 1,095 | 11 million   | \~11 GB  |

---

### 📂 With Index + BSON Overhead (\~20%)

| Traffic | Raw Size | +20% Overhead | Subtotal  |
| ------- | -------- | ------------- | --------- |
| Low     | 1.1 GB   | +0.22 GB      | \~1.32 GB |
| High    | 11 GB    | +2.2 GB       | \~13.2 GB |

---

### 🔁 With Replication (x3)

| Traffic | Subtotal  | Replicated Size |
| ------- | --------- | --------------- |
| Low     | \~1.32 GB | \~4 GB total    |
| High    | \~13.2 GB | \~40 GB total   |

---

## 🧮 Summary

| Traffic    | Events/3yrs | Est. MongoDB Size (w/ indexes, no compression) |
| ---------- | ----------- | ---------------------------------------------- |
| 1,000/day  | 1.1 million | \~4 GB (replica set total)                     |
| 10,000/day | 11 million  | \~40 GB (replica set total)                    |

---

## 🔧 Additional Considerations

* **WiredTiger compression** may reduce actual disk usage by 40–60%, especially for text-heavy logs.
* **Log compaction / archival** to cold storage (e.g., S3) after 3 years can help keep live MongoDB lean.
* If you use **hash chaining**, consider the performance of querying the latest record for each insert. You may optimize by buffering inserts in-memory or in Kafka and writing in batches.
* Use **MongoDB Atlas tier sizing** if you're deploying in the cloud. Based on the above, even M10 (10 GB) or M20 (20 GB) tiers will suffice.

Would you like a cost estimate for MongoDB Atlas or self-hosted based on this?

