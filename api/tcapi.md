{
  "productId": "12345",             // Identifier for the financial product or service
  "fields": ["APR", "APY", "fees"], // Optional: List of specific fields to retrieve
  "format": "json",                 // "json" for structured data, "pdf" for full document
  "language": "en",                 // Optional: Preferred language of terms
  "version": "latest"               // Optional: Specific version or "latest"
}

{
  "terms_and_conditions": {
    "productId": "12345",
    "lastUpdated": "2024-11-01",
    "effective_date": "2023-10-26",
    "applicable_fees": [
      {
        "fee_name": "Monthly Maintenance Fee",
        "fee_amount": 10.00,
        "fee_description": "Charged monthly for account maintenance."
      },
      {
        "fee_name": "Overdraft Fee",
        "fee_amount": 35.00,
        "fee_description": "Charged for each overdraft transaction."
      },
      {
        "fee_name": "Late Payment Fee",
        "fee_amount": 5.00,
        "fee_description": "Charged for late payment of mnthly maintenance fees."
      }
    ],
    "apr": 15.99,
    "apy": 16.50,
    "credit_limit": 5000.00,
    "rewards_program": {
      "name": "Rewards Plus",
      "description": "Earn points for every purchase.",
      "expiry": "24 months"
    },
    "overdraft_coverage": true,
    "arbitrationAgreement": {
      "applicable": true,
      "details": "All disputes will be resolved via arbitration."
    },
    "agreement_link": "https://www.examplebank.com/agreements/1234567890.json"
    "fullTermsLink": "https://example.com/terms/12345",
    "machineReadableLink": "https://example.com/api/v1/terms/12345.json"
  }
}
