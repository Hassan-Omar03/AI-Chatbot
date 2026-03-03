# API Examples and Testing

Complete examples for testing the Local AI Backend API.

## Testing with cURL

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "ollama_available": true,
  "knowledge_base_ready": true,
  "model": "llama2"
}
```

---

## 2. Chat Endpoint

### Basic Chat Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "user_id": "user123"
  }'
```

Response (Knowledge Base Match):
```json
{
  "response": "Our customer service is available Monday through Friday, 9:00 AM to 6:00 PM Eastern Standard Time. Outside these hours, you can submit a support request and we'll respond within 24 hours.",
  "confidence": 100.0,
  "intent": "hours",
  "source": "knowledge_base",
  "ticket_id": null
}
```

### LLM Response

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "user_id": "user123"
  }'
```

Response:
```json
{
  "response": "The capital of France is Paris. It is located in the north-central part of the country and is the largest city in France.",
  "confidence": 92.5,
  "intent": "information_request",
  "source": "llm",
  "ticket_id": null
}
```

---

## 3. Support Escalation

### Trigger Manual Support

```bash
curl -X POST http://localhost:8000/support-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "I have a complex issue that needs human support",
    "reason": "manual_escalation"
  }'
```

Response:
```json
{
  "ticket_id": "TKT-20240117123456-5678",
  "message": "I apologize, but I'm unable to provide a reliable answer to your question.\nA support ticket (ID: TKT-20240117123456-5678) has been created and our team will assist you shortly.\nPlease contact our support team for immediate assistance.",
  "timestamp": "2024-01-17T12:34:56.123456"
}
```

### Get Recent Support Tickets

```bash
curl http://localhost:8000/support/tickets?limit=5
```

Response:
```json
{
  "tickets": [
    {
      "id": "TKT-20240117123456-5678",
      "timestamp": "2024-01-17T12:34:56.123456",
      "user_message": "This is too complicated",
      "ai_response": "I'm not entirely sure about this...",
      "confidence_score": 45.2,
      "intent": "complaint",
      "reason": "low_confidence"
    }
  ],
  "total": 1
}
```

### Get Support Statistics

```bash
curl http://localhost:8000/support/stats
```

Response:
```json
{
  "total_escalations": 5,
  "escalations_by_reason": {
    "low_confidence": 4,
    "llm_unavailable": 1
  },
  "average_confidence": 62.3
}
```

---

## 4. Knowledge Base Management

### View All Knowledge Base Items

```bash
curl http://localhost:8000/knowledge-base
```

Response:
```json
{
  "items": [
    {
      "id": 1,
      "intent": "billing",
      "answer": "We offer multiple payment options...",
      "keywords": ["billing", "payment", "invoice"]
    },
    {
      "id": 2,
      "intent": "hours",
      "answer": "Our hours are Monday-Friday 9AM-6PM EST...",
      "keywords": ["hours", "open", "available"]
    }
  ],
  "total": 2
}
```

### Add New Knowledge Base Item

```bash
curl -X POST http://localhost:8000/knowledge-base/add \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "returns",
    "answer": "We accept returns within 30 days of purchase. Items must be in original condition with all packaging.",
    "keywords": ["return", "refund", "money back", "30 days"]
  }'
```

Response:
```json
{
  "status": "success",
  "message": "Added answer for intent: returns"
}
```

---

## Testing with Python

### Using requests library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print("System Status:", response.json())

# Send chat message
chat_response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "What is your return policy?",
        "user_id": "user123"
    }
)
result = chat_response.json()
print("\nAI Response:", result['response'])
print("Confidence:", result['confidence'], "%")
print("Source:", result['source'])

# Check support tickets
tickets = requests.get(f"{BASE_URL}/support/tickets")
print("\nRecent Tickets:", tickets.json()['total'])

# Add to knowledge base
kb_response = requests.post(
    f"{BASE_URL}/knowledge-base/add",
    json={
        "intent": "custom",
        "answer": "This is a custom answer",
        "keywords": ["custom", "test"]
    }
)
print("\nAdded to KB:", kb_response.json()['status'])
```

---

## Testing with JavaScript/Node.js

```javascript
const API_URL = "http://localhost:8000";

// Health check
async function checkHealth() {
  const response = await fetch(`${API_URL}/health`);
  const data = await response.json();
  console.log("System Status:", data);
}

// Send chat message
async function sendMessage(message) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      user_id: "user123"
    })
  });
  
  const data = await response.json();
  console.log("Response:", data.response);
  console.log("Confidence:", data.confidence + "%");
  console.log("Source:", data.source);
  
  return data;
}

// Get support tickets
async function getTickets() {
  const response = await fetch(`${API_URL}/support/tickets?limit=10`);
  const data = await response.json();
  console.log("Total Tickets:", data.total);
  console.log("Tickets:", data.tickets);
}

// Usage
checkHealth();
sendMessage("What is your return policy?");
getTickets();
```

---

## Testing with Postman

### Import Collection

Create a new Postman collection with these requests:

**1. Health Check**
- Method: GET
- URL: `http://localhost:8000/health`
- Headers: None

**2. Send Chat**
- Method: POST
- URL: `http://localhost:8000/chat`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "message": "What is your return policy?",
  "user_id": "user123"
}
```

**3. Get Tickets**
- Method: GET
- URL: `http://localhost:8000/support/tickets?limit=10`

**4. Get Stats**
- Method: GET
- URL: `http://localhost:8000/support/stats`

**5. Add to Knowledge Base**
- Method: POST
- URL: `http://localhost:8000/knowledge-base/add`
- Headers: `Content-Type: application/json`
- Body:
```json
{
  "intent": "test",
  "answer": "Test answer",
  "keywords": ["test"]
}
```

---

## Response Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (missing fields) |
| 422 | Validation error |
| 500 | Server error |

---

## Example Workflow

### Test Scenario: Customer Support Chatbot

```bash
#!/bin/bash

API="http://localhost:8000"

echo "1. Check system health..."
curl $API/health

echo -e "\n\n2. Test knowledge base response..."
curl -X POST $API/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are your hours?", "user_id":"test1"}'

echo -e "\n\n3. Test LLM response..."
curl -X POST $API/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How does AI work?", "user_id":"test1"}'

echo -e "\n\n4. View all support tickets..."
curl $API/support/tickets

echo -e "\n\n5. View statistics..."
curl $API/support/stats

echo -e "\n\n6. Add custom knowledge base item..."
curl -X POST $API/knowledge-base/add \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "custom_question",
    "answer": "This is a custom answer",
    "keywords": ["custom", "answer"]
  }'

echo -e "\n\nWorkflow complete!"
```

---

## Debugging Tips

1. **Enable verbose logging**: Add `LOG_LEVEL=DEBUG` to `.env`

2. **Check LLM status**: 
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Monitor response times**:
   ```bash
   curl -w "Time: %{time_total}s\n" http://localhost:8000/health
   ```

4. **Test knowledge base directly**:
   ```bash
   python
   >>> import json
   >>> with open('data/knowledge_base.json') as f:
   ...     kb = json.load(f)
   ...     print(kb)
   ```

5. **View server logs**: Check terminal where backend is running

---

## Load Testing

Simple load test script:

```python
import concurrent.futures
import requests
import time

API_URL = "http://localhost:8000/chat"

def make_request(message_id):
    try:
        response = requests.post(
            API_URL,
            json={
                "message": f"Test message {message_id}",
                "user_id": f"user_{message_id}"
            },
            timeout=30
        )
        return response.status_code, response.elapsed.total_seconds()
    except Exception as e:
        return None, str(e)

# Run 10 concurrent requests
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(make_request, range(10)))

duration = time.time() - start

print(f"Requests: {len(results)}")
print(f"Total time: {duration:.2f}s")
print(f"Avg time: {sum(r[1] for r in results if isinstance(r[1], float)) / len(results):.2f}s")
```

---

**Start with Health Check, then test Chat, then explore Support endpoints!**
