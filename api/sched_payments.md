{
  "scheduledPayments": [
    {
      "paymentId": "SP12345",
      "paymentType": "BILL_PAYMENT",
      "payee": {
        "name": "Acme Utility Company",
        "accountNumber": "XXXXXX1234",
        "contactInfo": {
          "email": "support@acmeutilities.com",
          "phone": "+1-800-123-4567"
        }
      },
      "amount": {
        "value": 55.25,
        "currency": "USD"
      },
      "scheduledDate": "2024-12-15",
      "status": "PENDING",
      "paymentMethod": "BANK_TRANSFER",
      "recurringDetails": null,
      "notification": {
        "reminder": true,
        "reminderDate": "2024-12-14",
        "deliveryMethod": "EMAIL"
      },
      "metadata": {
        "description": "Monthly utility bill for electricity.",
        "tags": ["utilities", "electricity"]
      },
      "auditTrail": {
        "createdBy": "user123",
        "createdDate": "2024-12-01T10:00:00Z",
        "lastUpdatedBy": "user123",
        "lastUpdatedDate": "2024-12-01T10:00:00Z"
      },
      "errorDetails": null
    },
    {
      "paymentId": "SP67890",
      "paymentType": "CREDIT_CARD_PAYMENT",
      "payee": {
        "name": "Data Provider Credit Card",
        "accountNumber": "XXXX XXXX XXXX 5678",
        "contactInfo": {
          "email": "support@datacredit.com",
          "phone": "+1-800-987-6543"
        }
      },
      "amount": {
        "value": 100.00,
        "currency": "USD"
      },
      "scheduledDate": "2024-12-22",
      "status": "SCHEDULED",
      "paymentMethod": "CREDIT_CARD",
      "recurringDetails": {
        "frequency": "MONTHLY",
        "endDate": "2025-12-22",
        "numberOfOccurrences": 12
      },
      "notification": {
        "reminder": true,
        "reminderDate": "2024-12-21",
        "deliveryMethod": "SMS"
      },
      "metadata": {
        "description": "Monthly credit card payment.",
        "tags": ["credit card", "finance"]
      },
      "auditTrail": {
        "createdBy": "user456",
        "createdDate": "2024-11-30T15:00:00Z",
        "lastUpdatedBy": "user456",
        "lastUpdatedDate": "2024-11-30T15:00:00Z"
      },
      "errorDetails": null
    }
  ]
}
