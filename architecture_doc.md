# System Architecture - AI Knowledge Copilot

## Overview

The Knowledge Copilot is built as a modern RAG (Retrieval-Augmented Generation) system with clean separation of concerns, focusing on production readiness, cost efficiency, and evaluation.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  Chat Widget   │  │ File Uploader  │  │ Settings Panel │  │
│  │  - Messages    │  │  - Drag/Drop   │  │  - Model Select│  │
│  │  - Streaming   │  │  - Progress    │  │  - Docs List   │  │
│  │  - Sources     │  │  - Validation  │  │  - Stats View  │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  │
│                                                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket / REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                              │
│                       (FastAPI)                                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   /upload    │  │    /chat     │  │    /stats    │        │
│  │   /delete    │  │  /documents  │  │   /health    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└──────┬──────────────────┬──────────────────┬───────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│   Prompt    │   │  RAG Engine  │   │     Cost     │
│  Manager    │   │              │   │   Logger     │
│             │   │              │   │              │
│ - System    │◄──┤ - Chunking   │   │ - Per Query  │
│ - Context   │   │ - Embeddings │──►│ - Per Model  │
│ - History   │   │ - Retrieval  │   │ - Latency    │
│ - Fallback  │   │              │   │ - Analytics  │
│             │   │              │   │              │
│ v1.0 v1.1   │   │              │   │              │
│ v1.2 (cur)  │   │              │   │              │
└─────────────┘   └──────┬───────┘   └──────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Vector Database    │
              │                      │
              │  FAISS / Chroma /    │
              │     Pinecone         │
              │                      │
              │  [Embeddings Index]  │
              │  [Metadata Store]    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Document Store     │
              │                      │
              │  - Original Docs     │
              │  - Chunks            │
              │  - Metadata          │
              └──────────────────────┘
```

---

## Component Deep Dive

### 1. Frontend (React/Next.js)

**Responsibilities:**
- User interaction and experience
- Real-time streaming display
- File upload management
- State management

**Key Technologies:**
- React 18 with hooks
- Tailwind CSS for styling
- Lucide React for icons
- EventSource/WebSocket for streaming

**Data Flow:**
```
User Input → Validation → API Request → Stream Handler → UI Update
```

---

### 2. API Gateway (FastAPI)

**Endpoints:**

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/upload` | POST | Process documents | 2-5s |
| `/chat` | POST | Query with streaming | 1-3s |
| `/documents` | GET | List documents | <100ms |
| `/delete/{id}` | DELETE | Remove document | <500ms |
| `/stats` | GET | System statistics | <100ms |
| `/health` | GET | Health check | <50ms |

**Middleware Stack:**
```
Request
  ↓
CORS Middleware (origin validation)
  ↓
Rate Limiting (optional)
  ↓
Authentication (optional)
  ↓
Request Logging
  ↓
Route Handler
  ↓
Error Handler
  ↓
Response
```

---

### 3. RAG Engine

**Architecture:**

```
┌─────────────────────────────────────────────────┐
│              RAG Engine Pipeline                │
│                                                 │
│  Document Input                                 │
│       ↓                                         │
│  ┌──────────────────┐                          │
│  │ Text Extraction  │ (PDF/MD/TXT)             │
│  └────────┬─────────┘                          │
│           ↓                                     │
│  ┌──────────────────┐                          │
│  │    Chunking      │ (500 chars, 50 overlap) │
│  │  - Sentence split │                          │
│  │  - Smart overlap  │                          │
│  └────────┬─────────┘                          │
│           ↓                                     │
│  ┌──────────────────┐                          │
│  │   Embedding      │ (Ada-002 or local)      │
│  │  - Generate vec  │                          │
│  │  - Normalize     │                          │
│  └────────┬─────────┘                          │
│           ↓                                     │
│  ┌──────────────────┐                          │
│  │  Vector Store    │ (FAISS index)           │
│  │  - Add to index  │                          │
│  │  - Store metadata│                          │
│  └──────────────────┘                          │
│                                                 │
│  Query Input                                    │
│       ↓                                         │
│  ┌──────────────────┐                          │
│  │ Query Embedding  │                          │
│  └────────┬─────────┘                          │
│           ↓                                     │
│  ┌──────────────────┐                          │
│  │ Vector Search    │ (Top-K, threshold)      │
│  │  - Similarity    │                          │
│  │  - Filtering     │                          │
│  └────────┬─────────┘                          │
│           ↓                                     │
│  ┌──────────────────┐                          │
│  │   Re-ranking     │ (optional)              │
│  └────────┬─────────┘                          │
│           ↓                                     │
│   Retrieved Context                             │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Vector Database Comparison:**

| Feature | FAISS | Chroma | Pinecone |
|---------|-------|--------|----------|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡⚡ |
| Scalability | 10K-100K | 100K-1M | 1M+ |
| Persistence | Manual | Built-in | Cloud |
| Cost | Free | Free | Paid |
| Setup | Easy | Easy | Medium |
| Production | Prototype | Small-Med | Enterprise |

---

### 4. Prompt Manager

**Version History:**

```
v1.0.0 (Basic)
├── System prompt: Role definition
├── No context handling
└── Generic responses

v1.1.0 (Enhanced)
├── Better context integration
├── Conversation history support
└── Citation requirements

v1.2.0 (Current - Production)
├── Advanced context layering
├── Fallback strategies
├── Tool selection logic
├── Summarization prompts
└── Confidence-based routing
```

**Prompt Construction Flow:**

```
User Query
    ↓
┌─────────────────────┐
│ Analyze Intent      │ (Procedural? Informational? Summary?)
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Select Strategy     │ (Search / Summarize / Explain)
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Retrieve Context    │ (RAG Engine)
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Check Confidence    │ < 0.7: Clarify | > 0.7: Answer
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Check Context Size  │ > 4K: Summarize | < 4K: Use Direct
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│ Build Final Prompt  │
│                     │
│ [System]            │
│ [Context]           │
│ [History]           │
│ [Query]             │
│ [Instructions]      │
└─────────┬───────────┘
          ↓
     LLM Response
```

---

### 5. Cost Logger

**Tracking Architecture:**

```
┌────────────────────────────────────────┐
│         Cost Tracking Flow             │
│                                        │
│  Request Start                         │
│       ↓                                │
│  ┌─────────────────┐                  │
│  │ Start Timer     │                  │
│  │ Count Tokens    │                  │
│  │ Log Metadata    │                  │
│  └────────┬────────┘                  │
│           ↓                            │
│  [Process Request]                     │
│           ↓                            │
│  ┌─────────────────┐                  │
│  │ End Timer       │                  │
│  │ Count Output    │                  │
│  │ Calculate Cost  │                  │
│  └────────┬────────┘                  │
│           ↓                            │
│  ┌─────────────────┐                  │
│  │ Log Entry       │                  │
│  │ - Model         │                  │
│  │ - Tokens        │                  │
│  │ - Cost (USD)    │                  │
│  │ - Latency       │                  │
│  │ - Timestamp     │                  │
│  └────────┬────────┘                  │
│           ↓                            │
│  ┌─────────────────┐                  │
│  │ Update Stats    │                  │
│  │ - Running total │                  │
│  │ - Averages      │                  │
│  │ - Aggregations  │                  │
│  └─────────────────┘                  │
│                                        │
└────────────────────────────────────────┘
```

**Log Entry Format:**

```json
{
  "request_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "model": "claude-sonnet-4",
  "input_tokens": 2000,
  "output_tokens": 500,
  "input_cost": 0.006,
  "output_cost": 0.0075,
  "total_cost": 0.0135,
  "latency_seconds": 1.8,
  "success": true
}
```

---

## Data Models

### Document Model

```python
{
  "doc_id": "uuid",
  "filename": "deployment-guide.md",
  "content": "full text...",
  "metadata": {
    "size": 15420,
    "type": "text/markdown",
    "uploaded_at": "2024-01-15T10:00:00Z",
    "uploaded_by": "user@company.com"
  },
  "chunks": [
    {
      "chunk_id": 0,
      "text": "chunk content...",
      "embedding": [0.123, -0.456, ...],
      "token_count": 125
    }
  ]
}
```

### Conversation Model

```python
{
  "conversation_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "How do we deploy?",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Based on deployment-guide.md...",
      "sources": ["deployment-guide.md"],
      "confidence": 0.87,
      "cost": 0.0135,
      "latency": 1.8,
      "timestamp": "2024-01-15T10:30:02Z"
    }
  ],
  "metadata": {
    "total_messages": 10,
    "total_cost": 0.15,
    "avg_confidence": 0.82
  }
}
```

---

## Deployment Strategies

### Option 1: Single Server (Prototype)

```
[Load Balancer]
      ↓
[EC2 / VPS]
  ├── Frontend (Nginx)
  ├── Backend (Uvicorn)
  ├── Vector DB (FAISS)
  └── Storage (Local)
```

**Pros:** Simple, cheap, fast setup
**Cons:** No scaling, single point of failure
**Cost:** $20-50/month

---

### Option 2: Containerized (Recommended)

```
[Load Balancer]
      ↓
[Kubernetes / ECS]
  ├── Frontend Pods (3x)
  ├── Backend Pods (5x)
  ├── Redis Cache
  └── Shared Storage (S3/EFS)
      ↓
[Managed Vector DB]
  └── Pinecone / Weaviate
```

**Pros:** Scalable, resilient, professional
**Cons:** More complex, higher cost
**Cost:** $200-500/month

---

### Option 3: Serverless (Cost-Optimized)

```
[CloudFront]
      ↓
[S3 Static Site]
      ↓
[API Gateway]
      ↓
[Lambda Functions]
      ↓
[Pinecone + S3]
```

**Pros:** Auto-scaling, pay per use
**Cons:** Cold starts, limits
**Cost:** $50-150/month (usage-based)

---

## Security Considerations

### 1. Authentication Flow

```
User Request
    ↓
API Gateway
    ↓
JWT Validation
    ↓
[Valid?] ─No→ 401 Unauthorized
    ↓ Yes
Rate Limit Check
    ↓
[OK?] ─No→ 429 Too Many Requests
    ↓ Yes
Process Request
    ↓
Response
```

### 2. Data Protection

- **At Rest:** Encrypt documents (AES-256)
- **In Transit:** TLS 1.3 for all connections
- **API Keys:** Environment variables, never in code
- **PII Handling:** Detect and redact sensitive data

### 3. Access Control

```python
permissions = {
  "admin": ["read", "write", "delete", "manage_users"],
  "user": ["read", "write"],
  "viewer": ["read"]
}
```

---

## Monitoring & Observability

### Metrics to Track

```
Application Metrics:
├── Request Rate (req/sec)
├── Error Rate (%)
├── P95 Latency (ms)
└── Success Rate (%)

Business Metrics:
├── Active Users
├── Queries per User
├── Documents Indexed
└── Cost per Query

System Metrics:
├── CPU Usage (%)
├── Memory Usage (MB)
├── Disk I/O
└── Network Traffic
```

### Logging Strategy

```
Level: INFO (production) / DEBUG (development)

Structured Logs:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "rag-engine",
  "event": "document_indexed",
  "doc_id": "uuid",
  "chunks": 47,
  "duration_ms": 1234
}
```

---

## Performance Optimization

### 1. Caching Strategy

```
┌──────────────┐
│ Redis Cache  │
│              │
│ Layer 1: Query Results (1 hour TTL)
│ Layer 2: Document Chunks (24 hour TTL)
│ Layer 3: Embeddings (permanent)
└──────────────┘
```

### 2. Database Optimization

```sql
-- Index on frequently queried fields
CREATE INDEX idx_doc_filename ON documents(filename);
CREATE INDEX idx_chunk_doc_id ON chunks(doc_id);

-- Materialized view for stats
CREATE MATERIALIZED VIEW stats_summary AS
  SELECT DATE(timestamp) as date,
         COUNT(*) as requests,
         AVG(latency) as avg_latency
  FROM request_logs
  GROUP BY DATE(timestamp);
```

### 3. Query Optimization

- **Batch Embeddings:** Process 10-50 at once
- **Async Processing:** Non-blocking I/O
- **Connection Pooling:** Reuse DB connections
- **Lazy Loading:** Load chunks on demand

---

## Scaling Considerations

### Horizontal Scaling

```
Documents: 1K → 10K → 100K → 1M
    ↓          ↓        ↓        ↓
FAISS     Chroma   Pinecone  Pinecone
                             + Sharding
```

### Vertical Scaling

```
Traffic: 10 req/s → 100 req/s → 1000 req/s
    ↓                ↓              ↓
1 Backend        5 Backends    Load Balancer
                               + Auto-scaling
```

---

## Disaster Recovery

### Backup Strategy

```
Daily Backups:
├── Vector Index → S3
├── Documents → S3
├── Logs → CloudWatch/S3
└── Database → RDS Snapshots

Recovery Time Objective (RTO): < 1 hour
Recovery Point Objective (RPO): < 24 hours
```

---

This architecture is designed to evolve from prototype to production seamlessly. Start with FAISS and single-server deployment, then migrate to managed services as you scale.