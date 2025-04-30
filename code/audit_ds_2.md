You're absolutely right to be concerned about that. Querying the latest record for every insert would create a bottleneck and potential race conditions in high-traffic scenarios. Here's a better approach:

## Optimized Tamper-Proofing Without Per-Insert Queries

### Solution 1: In-Memory Hash Chain State (For Single Consumer)

```python
# Maintain hash chain state in memory
class AuditProcessor:
    def __init__(self):
        self.last_hash = sha256("system_seed")  # Initial value
    
    def process_event(self, event):
        new_hash = self.calculate_hash(event, self.last_hash)
        
        record = {
            **event,
            "hashChain": new_hash,
            "previousHash": self.last_hash
        }
        
        # Optimistic insert - we assume we're the only writer
        mongo.insert(record)
        
        # Update state only after successful write
        self.last_hash = new_hash
```

### Solution 2: Partitioned Hash Chains (For Multiple Consumers)

```python
# Partition by customer/entity to allow parallel processing
def process_event(event):
    customer_id = event["customerId"]
    
    # Get last hash atomically using findAndModify
    last_record = mongo.collection.find_and_modify(
        query={"customerId": customer_id},
        sort=[("timestamp", -1)],
        update={"$set": {"lock": True}},
        new=True
    )
    
    previous_hash = last_record["hashChain"] if last_record else initial_hash(customer_id)
    
    new_hash = calculate_hash(event, previous_hash)
    
    mongo.insert({
        **event,
        "hashChain": new_hash,
        "previousHash": previous_hash
    })
```

### Solution 3: Batch Processing with Post-Verification (Most Scalable)

```python
def process_batch(events):
    # Get the most recent hash once per batch
    last_record = mongo.collection.find_one(
        {}, 
        sort=[("timestamp", -1)],
        projection={"hashChain": 1}
    )
    previous_hash = last_record["hashChain"] if last_record else system_seed
    
    # Build chain within batch
    records = []
    for event in events:
        new_hash = calculate_hash(event, previous_hash)
        records.append({
            **event,
            "hashChain": new_hash,
            "previousHash": previous_hash
        })
        previous_hash = new_hash
    
    # Bulk insert
    mongo.bulk_insert(records)
    
    # Asynchronous verification
    verify_last_records(len(events))
```

## Race Condition Handling

For true multi-writer scenarios:

```python
def safe_insert(event):
    while True:
        try:
            # Atomic operation using $isolated
            result = mongo.collection.find_and_modify(
                query={"_id": "chain_state"},
                update={"$set": {"last_hash": new_hash}},
                upsert=True,
                new=True
            )
            break
        except WriteConflict:
            sleep(random_interval())
```

## Recommended Approach for 1M+/day:

1. **Partitioned Hash Chains**:
   - Shard by customer ID or entity ID
   - Each partition maintains its own chain

2. **Batch Processing**:
   - Process 100-1000 events at a time
   - Maintain chain state within the batch
   - Periodically verify chain integrity

3. **Fallback Verification**:
   ```python
   def verify_window(start_time, end_time):
       window = mongo.find({"timestamp": {"$gte": start_time, "$lte": end_time}})
                      .sort("timestamp", 1)
       
       for i in range(1, len(window)):
           if window[i]["previousHash"] != window[i-1]["hashChain"]:
               trigger_alert()
   ```

This eliminates the per-insert query bottleneck while maintaining tamper-evident properties. The system can scale horizontally by processing different customer partitions in parallel.
