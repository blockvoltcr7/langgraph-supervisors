# Limitless OS - API Endpoints Specification

**Complete REST and Streaming API documentation**

---

## Architecture Overview

### **API Layers**
- **Next.js API Routes** (Vercel) - Authentication, campaign management, document uploads
- **Python Backend** (Google Cloud / Vercel) - LangGraph agent execution
- **Supabase** - Database queries, authentication

### **Communication Pattern**
```
Next.js Frontend (Vercel AI SDK)
    ↕ (HTTP + SSE)
Python LangGraph Backend
    ↕ (PostgreSQL)
Supabase Database
```

---

## Authentication

### **Owner Authentication**
- **Provider**: Supabase Auth
- **Method**: JWT tokens
- **Flow**: Next.js middleware validates tokens

```typescript
// Protected route example
headers: {
  'Authorization': 'Bearer eyJhbGc...'
}
```

---

## Next.js API Routes

### **1. Campaign Management**

#### **POST /api/campaigns/create**
Create a new campaign

**Request**:
```json
{
  "name": "Instagram Ads - Jan 2025",
  "description": "Winter campaign targeting fitness coaches",
  "max_uses": 100,
  "expires_at": "2025-02-28T23:59:59Z"
}
```

**Response**:
```json
{
  "success": true,
  "campaign": {
    "id": "camp_abc123",
    "code": "ABC123",
    "name": "Instagram Ads - Jan 2025",
    "url": "https://limitlessos.com/chat/ABC123",
    "qr_code_url": "https://storage.googleapis.com/qr/ABC123.png",
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

**Errors**:
- `400` - Invalid input
- `401` - Unauthorized
- `409` - Campaign code already exists

---

#### **GET /api/campaigns**
List all campaigns

**Query Params**:
- `status` (optional): "active" | "expired" | "all"
- `limit` (optional): number (default: 50)
- `offset` (optional): number (default: 0)

**Response**:
```json
{
  "campaigns": [
    {
      "id": "camp_abc123",
      "code": "ABC123",
      "name": "Instagram Ads - Jan 2025",
      "total_clicks": 150,
      "total_conversations": 45,
      "total_qualified": 30,
      "total_conversions": 8,
      "conversion_rate": 0.178,
      "is_active": true,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 10,
  "has_more": false
}
```

---

#### **GET /api/campaigns/:code/analytics**
Get campaign analytics

**Response**:
```json
{
  "campaign": {
    "code": "ABC123",
    "name": "Instagram Ads - Jan 2025"
  },
  "metrics": {
    "total_clicks": 150,
    "total_conversations": 45,
    "total_qualified": 30,
    "total_conversions": 8,
    "conversion_rate": 0.178,
    "avg_messages_per_conversation": 12.5,
    "avg_time_to_qualification": "5 minutes",
    "top_objections": [
      {"type": "price", "count": 15},
      {"type": "time", "count": 8}
    ]
  },
  "timeline": [
    {"date": "2025-01-15", "clicks": 20, "conversations": 5, "conversions": 1},
    {"date": "2025-01-16", "clicks": 25, "conversations": 8, "conversions": 2}
  ]
}
```

---

### **2. Document Management**

#### **POST /api/documents/upload**
Upload a document

**Request** (multipart/form-data):
```
file: File (PDF, DOCX, TXT, MD)
category: string (optional)
tags: string[] (optional)
```

**Response**:
```json
{
  "success": true,
  "document": {
    "id": "doc_xyz789",
    "filename": "pitch_scripts.pdf",
    "file_size": 524288,
    "storage_url": "https://storage.googleapis.com/...",
    "processing_status": "pending",
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

**Processing Flow**:
1. Upload to Google Cloud Storage
2. Insert metadata to Supabase
3. Trigger Python worker for embedding generation
4. Update status to "completed"

---

#### **GET /api/documents**
List uploaded documents

**Response**:
```json
{
  "documents": [
    {
      "id": "doc_xyz789",
      "filename": "pitch_scripts.pdf",
      "category": "pitch",
      "processing_status": "completed",
      "embeddings_created": true,
      "total_chunks": 45,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

#### **DELETE /api/documents/:id**
Delete a document

**Response**:
```json
{
  "success": true,
  "message": "Document and embeddings deleted"
}
```

---

### **3. Conversation Management**

#### **GET /api/conversations**
List conversations

**Query Params**:
- `campaign_id` (optional): Filter by campaign
- `stage` (optional): Filter by stage
- `qualified` (optional): Filter by qualification status
- `limit`, `offset`: Pagination

**Response**:
```json
{
  "conversations": [
    {
      "id": "lead-fitcoach_mike-a1b2c3d4",
      "instagram_handle": "@fitcoach_mike",
      "campaign_code": "ABC123",
      "current_stage": "closing",
      "qualified": true,
      "qualification_score": 0.85,
      "total_messages": 9,
      "created_at": "2025-01-15T10:00:00Z",
      "last_message_at": "2025-01-15T10:15:00Z"
    }
  ]
}
```

---

#### **GET /api/conversations/:id/transcript**
Get conversation transcript

**Response**:
```json
{
  "conversation": {
    "id": "lead-fitcoach_mike-a1b2c3d4",
    "instagram_handle": "@fitcoach_mike"
  },
  "messages": [
    {
      "role": "ai",
      "content": "Hey there! Are you a coach in health, fitness, wellness, or mindset?",
      "timestamp": "2025-01-15T10:00:00Z"
    },
    {
      "role": "human",
      "content": "Yes, I'm a fitness coach",
      "timestamp": "2025-01-15T10:00:30Z"
    }
  ]
}
```

---

### **4. Analytics**

#### **GET /api/analytics/dashboard**
Get owner dashboard metrics

**Response**:
```json
{
  "summary": {
    "total_campaigns": 5,
    "active_conversations": 12,
    "total_qualified_today": 8,
    "total_conversions_today": 2,
    "conversion_rate_today": 0.167,
    "revenue_today": 994
  },
  "recent_conversions": [
    {
      "instagram_handle": "@fitcoach_mike",
      "plan": "option2",
      "amount": 497,
      "completed_at": "2025-01-15T11:30:00Z"
    }
  ]
}
```

---

## Python Backend API (LangGraph)

### **Base URL**
- **Development**: `http://localhost:8000`
- **Production**: `https://langgraph-api.limitlessos.com`

---

### **1. Chat (Streaming)**

#### **POST /api/chat/stream**
Send message and stream AI response

**Request**:
```json
{
  "campaign_code": "ABC123",
  "instagram_handle": "@fitcoach_mike",
  "message": "Yes, I'm a fitness coach"
}
```

**Response** (Server-Sent Events):
```
event: message
data: {"type": "token", "content": "Awesome"}

event: message
data: {"type": "token", "content": "! What"}

event: message
data: {"type": "token", "content": " type"}

event: done
data: {"type": "complete", "thread_id": "lead-fitcoach_mike-a1b2c3d4"}
```

**Implementation** (Vercel AI SDK):
```typescript
import { streamText } from 'ai';

const response = await fetch('/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ campaign_code, instagram_handle, message })
});

const stream = response.body;
// Vercel AI SDK handles streaming
```

---

### **2. Chat (Non-Streaming)**

#### **POST /api/chat**
Send message and get complete response

**Request**:
```json
{
  "campaign_code": "ABC123",
  "instagram_handle": "@fitcoach_mike",
  "message": "Yes, I'm a fitness coach"
}
```

**Response**:
```json
{
  "thread_id": "lead-fitcoach_mike-a1b2c3d4",
  "message": "Awesome! What type of fitness coaching do you offer right now?",
  "current_stage": "qualification",
  "metadata": {
    "agent": "qualifier_agent",
    "questions_asked": 1
  }
}
```

---

### **3. Validate Campaign**

#### **GET /api/campaigns/:code/validate**
Validate campaign code before starting chat

**Response**:
```json
{
  "valid": true,
  "campaign": {
    "code": "ABC123",
    "name": "Instagram Ads - Jan 2025",
    "expires_at": "2025-02-28T23:59:59Z",
    "is_active": true
  }
}
```

**Errors**:
- `404` - Campaign not found
- `410` - Campaign expired

---

### **4. Resume Conversation**

#### **GET /api/conversations/:thread_id/state**
Get current conversation state

**Response**:
```json
{
  "thread_id": "lead-fitcoach_mike-a1b2c3d4",
  "current_stage": "qualification",
  "qualified": false,
  "questions_asked": 2,
  "business_type": "fitness coaching",
  "monthly_revenue": "$5K",
  "last_message": "Around $5K per month",
  "next_prompt": "How are you currently getting clients?"
}
```

---

## Webhooks

### **1. Stripe Payment Webhook**

#### **POST /api/webhooks/stripe**
Receive Stripe payment events

**Request** (from Stripe):
```json
{
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_a1b2c3d4",
      "customer": "cus_abc123",
      "metadata": {
        "thread_id": "lead-fitcoach_mike-a1b2c3d4",
        "campaign_code": "ABC123",
        "instagram_handle": "@fitcoach_mike"
      },
      "amount_total": 49700,
      "payment_status": "paid"
    }
  }
}
```

**Processing**:
1. Verify Stripe signature
2. Extract metadata
3. Update conversation (payment_completed: true)
4. Insert payment record
5. Update campaign stats
6. Trigger onboarding email

**Response**:
```json
{
  "received": true
}
```

---

## Error Responses

### **Standard Error Format**

```json
{
  "error": {
    "code": "CAMPAIGN_NOT_FOUND",
    "message": "Campaign code ABC123 does not exist",
    "details": {
      "campaign_code": "ABC123"
    }
  }
}
```

### **Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing auth token |
| `CAMPAIGN_NOT_FOUND` | 404 | Campaign code doesn't exist |
| `CAMPAIGN_EXPIRED` | 410 | Campaign has expired |
| `CAMPAIGN_LIMIT_REACHED` | 429 | Campaign max uses reached |
| `INVALID_INPUT` | 400 | Validation error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

### **Limits**

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/chat` | 10 req/min | Per Instagram handle |
| `/api/campaigns` | 100 req/min | Per owner |
| `/api/documents/upload` | 10 req/hour | Per owner |

### **Headers**

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642262400
```

---

## Testing Endpoints

### **Development**

```bash
# Validate campaign
curl http://localhost:3000/api/campaigns/ABC123/validate

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"campaign_code": "ABC123", "instagram_handle": "@test", "message": "Hello"}'
```

### **Production**

```bash
# With authentication
curl https://api.limitlessos.com/campaigns \
  -H "Authorization: Bearer eyJhbGc..."
```

---

**This API specification provides the complete interface between frontend, backend, and external services.**
