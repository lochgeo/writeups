To deliver alerts from your Python backend to Microsoft Teams as chat messages, the **best and simplest approach** is to use **Incoming Webhooks** in Microsoft Teams.

---

### ✅ Why Incoming Webhooks?
- **Easy to set up** (no OAuth, no app registration needed initially).
- **Direct integration** into a specific Teams channel.
- **Lightweight** — just an HTTP POST from your Python backend.
- **Free to use** with your existing Microsoft 365/Teams setup.

---

### 🔧 Step-by-Step: Set Up Incoming Webhook in Teams

1. **Go to the desired Teams channel**:
   - Open Microsoft Teams.
   - Navigate to the team and channel where you want alerts to appear.

2. **Add the "Incoming Webhook" connector**:
   - Click on the **"..." (More options)** in the channel header.
   - Select **"Connectors"**.
   - Search for **"Incoming Webhook"**, click **"Add"**.
   - Give it a name (e.g., "Alert Bot") and optionally upload an icon.
   - Click **"Create"**.
   - Copy the **webhook URL** (this is your endpoint — keep it secure!).

3. **Test the webhook (optional)**:
   - Use `curl` or Python to send a test message.

---

### 🐍 Python Code to Send Alert to Teams

Use the `requests` library to POST a JSON payload to the webhook URL.

```python
import requests

def send_teams_alert(webhook_url, title, message, color="E74C3C"):  # red color
    payload = {
        "title": title,
        "text": message,
        "themeColor": color  # Hex color code
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code == 200:
        print("Alert sent to Teams successfully.")
    else:
        print(f"Failed to send alert. Status: {response.status_code}, {response.text}")

# Usage
WEBHOOK_URL = "https://yourcompany.webhook.office.com/webhookb2/..."  # Your webhook URL
send_teams_alert(WEBHOOK_URL, "High Priority Alert", "CPU usage exceeded 90%!")
```

---

### 📝 Teams Message Formatting (Optional Enhancements)

You can enrich messages using **Adaptive Cards** or more advanced JSON. Example with sections and facts:

```python
payload = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "0076D7",
    "summary": "Alert",
    "sections": [{
        "activityTitle": "🚨 System Alert",
        "facts": [
            {"name": "Service", "value": "Database"},
            {"name": "Status", "value": "Down"},
            {"name": "Time", "value": "2025-04-05 10:00 UTC"}
        ],
        "text": "Please investigate immediately."
    }]
}
```

> Note: This format uses the **Office 365 Connector Card** schema, which is what Incoming Webhooks support by default.

---

### 🔐 Security & Best Practices

- **Store the webhook URL securely** (e.g., environment variable):
  ```python
  import os
  WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
  ```

- **Rotate the webhook** if exposed (just delete and recreate in Teams).

- **Rate limiting**: Avoid spamming. Teams may throttle messages.

- **Error handling**: Always check response status.

---

### 🚀 Advanced Option (Optional)

If you need more control (e.g., sending to users, using bots, rich interactions), consider the **Microsoft Graph API** with a registered app and OAuth. But this is **overkill for simple alerts**.

👉 Use **Incoming Webhook** unless you need user-specific chats or bot interactions.

---

### ✅ Summary

| Feature | Supported |
|-------|-----------|
| Easy setup | ✅ Yes |
| No auth tokens | ✅ Yes |
| Works with Python backend | ✅ Yes |
| Rich formatting | ✅ (Limited, but sufficient) |
| Real-time alerts | ✅ Yes |

---

✅ **Recommended Path**:
Use **Incoming Webhook** with a simple `requests.post()` in your Python backend.

Let me know if you want to send alerts to **private chats** (requires Graph API) or use **custom formatting/icons**!
