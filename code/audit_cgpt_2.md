Based on the regulation you provided (1033.351), there **are several implications for the audit event payload schema** to ensure compliance. The core requirement is that **audit events must act as evidence of compliance with data access, denial, revocation, and retention** obligations. Therefore, your existing audit event schema should be **extended and structured to capture specific fields and event types** as mandated by the regulation.

### 🔧 Required Enhancements to the Audit Event Payload Schema:

1. **Event Type Classification**

   * You need to clearly distinguish between different event categories:

     * `access_request` (e.g., third party request to developer interface)
     * `access_denial` (with reasons under § 1033.321)
     * `information_request` and `information_denial` (under § 1033.331)
     * `authorization_provided` and `authorization_revoked` (under § 1033.401)
     * `performance_record` (for availability/performance tracking)
     * `policy_updated` (when policies/procedures are updated)
     * `disclosure_provided` (under § 1033.341)

2. **Denial and Response Metadata**

   * For every `*_denial` event, include:

     * `denial_reason_code`
     * `denial_reason_description`
     * `recipient` (consumer, third party, aggregator)
     * `communication_method` (email, API response, portal)
     * `timestamp_of_response`

3. **Retention Tagging**

   * Every event should include:

     * `retention_category` (to map how long it should be retained, generally 3 years)
     * `response_context_id` (to link multiple events, like request + denial)
     * `interface_type` (e.g., developer interface, consumer interface)

4. **Data Field Visibility Log**

   * When applicable, audit events should record:

     * `data_fields_requested`
     * `data_fields_denied`
     * `reason_for_omission` (referring to exceptions under § 1033.221)
     * `standard_conformance` (e.g., "FAPI-compliant")

5. **Authorization and Revocation Tracking**

   * Store:

     * `consumer_id`
     * `third_party_id`
     * `aggregator_id` (if applicable)
     * `authorization_method`
     * `revocation_method`
     * `effective_timestamp`

---

### 🧩 Example Extended Audit Event Schema (JSON)

```json
{
  "eventType": "access_denial",
  "timestamp": "2025-04-30T10:45:00Z",
  "sourceApp": "consent-management",
  "consumerId": "cus_123",
  "thirdPartyId": "tp_456",
  "aggregatorId": "agg_789",
  "requestId": "req_001",
  "responseContextId": "ctx_001",
  "denialReasonCode": "NO_AUTH",
  "denialReasonDescription": "Third party did not present valid authorization",
  "communicationMethod": "API",
  "dataFieldsRequested": ["account.balance", "account.transactions"],
  "dataFieldsDenied": ["account.transactions"],
  "retentionCategory": "reg_1033.351_d1i",
  "interfaceType": "developer",
  "hash": "abc123...",
  "prevHash": "xyz987..."
}
```

---

### ✅ Summary

To comply with §1033.351, your audit system must:

* Log all access/denial/authorization/revocation events with **explicit context and substantiating metadata**
* Retain these logs for **at least three years**
* Ensure logs are structured in a way that supports easy compliance auditing, verification, and reporting

Would you like a tabular breakdown of the new fields along with their data types and when to populate them?
