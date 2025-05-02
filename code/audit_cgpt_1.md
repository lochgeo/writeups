The proposed solution is a centralized audit logging system designed to ingest audit events from multiple microservices (e.g., login, consent, payments) through Kafka and store them in a tamper-evident and queryable format in MongoDB. Each service posts structured audit events to a Kafka topic, which are then consumed by a Kafka consumer that validates, enriches, and inserts them into MongoDB. The events include rich context, such as customer, third party, or aggregator identifiers, along with metadata like timestamps, event types, and action details. MongoDB collections are indexed for fast queries and configured with TTL (time-to-live) indexing to automatically expire records after three years, ensuring compliance with data retention policies while keeping storage costs low.

To ensure data integrity and tamper-evidence, the system uses a hash chaining mechanism—each audit record includes a cryptographic hash of its contents combined with the hash of the previous record. To avoid contention under high write volumes, hash chains are scoped per logical partition (e.g., per source app per day), and latest hashes are tracked in-memory or in a fast store like Redis. This maintains verifiability while supporting high throughput. A console UI enables support and compliance users to search audit logs, trace user activity, and verify event integrity. Optional cold archiving (e.g., to S3) of older data enables further cost optimization without sacrificing long-term accessibility.

Capture audit events from multiple services (login, consent, payments, etc.)

Maintain rich context (customer, third party, aggregator)

Ensure data immutability and tamper resistance

Retain data for 3 years and purge automatically

Provide query interface for support, compliance, and investigation teams

Be cost-effective and scalable for write-heavy workloads
