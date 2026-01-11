# 🔥 AI Knowledge Copilot for Internal Teams

A production-ready RAG (Retrieval-Augmented Generation) system for internal team documentation, combining the power of vector search with LLM intelligence.

**Think Notion/Confluence + ChatGPT, but scoped, opinionated, and built for teams.**

## 🎯 What It Does

Upload your team's documentation (PDFs, Markdown, Notion exports) and get instant, context-aware answers grounded in your actual documents. No hallucinations, no generic responses—just accurate information from your knowledge base.

### Key Features

- **Smart Document Processing**: Automatic chunking with overlap for better context
- **Vector-Based Retrieval**: FAISS/Chroma/Pinecone for fast, relevant search
- **Streaming Responses**: Real-time token-by-token responses
- **Confidence Scoring**: Know when answers are uncertain
- **Source Attribution**: Every answer cites its sources
- **Conversation Memory**: Multi-turn conversations with context
- **Cost Tracking**: Monitor API usage and optimize spending
- **Prompt Versioning**: Track and iterate on prompt engineering

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Chat UI      │  │ Doc Upload   │  │ File Manager │     │
│  │ (Streaming)  │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI Backend │
                    │  (Python)        │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐      ┌────────▼────────┐    ┌─────▼─────┐
   │ Prompt  │      │   RAG Engine     │    │   Cost    │
   │ Manager │      │                  │    │  Logger   │
   │         │      │ ┌──────────────┐ │    │           │
   │ - V1.0  │      │ │ Chunking     │ │    │ - Tokens  │
   │ - V1.1  │◄─────┤ │ Embeddings   │ │    │ - Latency │
   │ - V1.2  │      │ │ Vector Store │ │    │ - Pricing │
   └─────────┘      │ └──────────────┘ │    └───────────┘
                    │                  │
                    │ ┌──────────────┐ │
                    │ │ FAISS Index  │ │
                    │ │ (or Chroma/  │ │
                    │ │  Pinecone)   │ │
                    │ └──────────────┘ │
                    └──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   LLM API       │
                    │ (Claude/GPT-4)  │
                    └─────────────────┘
```

### Data Flow

1. **Document Upload** → Text extraction → Chunking → Embedding generation → Vector store
2. **User Query** → Query embedding → Vector similarity search → Context retrieval
3. **Prompt Construction** → System prompt + Retrieved context + Conversation history + User query
4. **LLM Response** → Streaming tokens → Source attribution → Cost logging

---

## 🚀 Quick Start

### Prerequisites

```bash
python 3.9+
node 18+
```

### Backend Setup

```bash
# Clone and navigate
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"  # for embeddings

# Run server
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# UI available at http://localhost:3000
```

### Docker Setup (Recommended)

```bash
# Build and run all services
docker-compose up

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

---

## 📁 Project Structure

```
knowledge-copilot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── rag_engine.py           # RAG implementation
│   ├── prompt_manager.py       # Prompt versioning & templates
│   ├── cost_logger.py          # Usage tracking
│   ├── evaluator.py            # Response evaluation
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 💡 Prompt Design Decisions

### 1. **Layered Context Architecture**

```python
PROMPT = f"""
{SYSTEM_PROMPT}           # Role, capabilities, constraints
{RETRIEVED_CONTEXT}       # Top-K most relevant chunks
{CONVERSATION_HISTORY}    # Last N messages for continuity
{USER_QUERY}              # Current question
{RESPONSE_INSTRUCTIONS}   # Output formatting, citations
"""
```

**Why?** Clear separation of concerns makes debugging easier and allows independent optimization of each layer.

### 2. **Confidence-Based Fallbacks**

```python
if retrieval_score < 0.7:
    return clarification_prompt()
elif context_length > 4000:
    return summarize_then_answer()
else:
    return standard_answer()
```

**Why?** Prevents hallucinations by acknowledging when information is insufficient. Better user experience than wrong answers.

### 3. **Prompt Versioning Strategy**

- `v1.0`: Basic system prompt
- `v1.1`: Added context handling
- `v1.2`: Tool selection + summarization (current)

**Why?** Track what works, A/B test prompts, rollback if needed. Essential for continuous improvement.

### 4. **Source Citation Template**

```
Response: [Your answer here]

Sources:
- document.pdf (chunk 3, confidence: 0.87)
- guide.md (chunk 12, confidence: 0.82)
```

**Why?** Builds trust, enables verification, helps debug retrieval quality.

---

## ⚖️ Tradeoffs & Design Decisions

### 1. **Vector DB: FAISS vs Chroma vs Pinecone**

| Choice | Pros | Cons | When to Use |
|--------|------|------|-------------|
| **FAISS** ✓ | Fast, in-memory, no external deps | No built-in persistence, manual management | < 10k documents, prototype |
| **Chroma** | Easy setup, persistence, metadata | Slower than FAISS, local only | Small-medium teams (10-100k docs) |
| **Pinecone** | Managed, scalable, low latency | Cost, vendor lock-in | Production, > 100k docs |

**Our Choice: FAISS** (easy to switch later)
- Fastest for prototypes
- Zero infrastructure
- Can migrate to Chroma/Pinecone when needed

### 2. **Chunking Strategy: 500 chars with 50 char overlap**

**Why 500 chars?**
- Balances context granularity with retrieval precision
- ~125 tokens per chunk (fits embedding limits)
- Small enough for specific retrieval, large enough for coherent context

**Why 50 char overlap?**
- Prevents information loss at boundaries
- Ensures sentences aren't split awkwardly
- Minimal storage overhead (~10%)

**Tradeoff:**
- More chunks = better precision, higher storage/compute
- Fewer chunks = faster search, risk missing info

### 3. **Model Choice: Claude Sonnet 4 (default)**

```python
MODELS = {
    "fast": "claude-haiku-4",      # Low cost, quick answers
    "balanced": "claude-sonnet-4",  # Best price/performance ✓
    "powerful": "claude-opus-4"     # Complex reasoning
}
```

**Cost Comparison (per 1M tokens):**
- Haiku: $0.25 input / $1.25 output
- Sonnet: $3 input / $15 output
- Opus: $15 input / $75 output

**Our Default: Sonnet**
- 10x cheaper than Opus
- Only 2x slower than Haiku
- Sufficient for 90% of queries

### 4. **Streaming vs Batch Responses**

**Streaming (default):**
- Better UX (perceived speed)
- Shows progress immediately
- Can't retry on failure

**Batch:**
- Easier error handling
- Can cache entire response
- Feels slower to users

**Tradeoff:** We default to streaming but support both.

### 5. **Context Window Management**

```python
if len(context) > 4000 chars:
    context = summarize(context)  # Compress to ~1000 chars
```

**Why summarize vs truncate?**
- Preserves key information
- Better than cutting mid-sentence
- Costs ~$0.01 extra per query

**Tradeoff:** Small cost increase for better quality.

---

## 📊 Cost Analysis

### Typical Query Breakdown

```
Document Upload (one-time):
├─ Text extraction: Free
├─ Chunking: Free
└─ Embeddings (ada-002): $0.0001/1K tokens
   └─ 10-page PDF → ~5000 tokens → $0.0005

Query Processing:
├─ Query embedding: $0.0001
├─ Vector search: Free (FAISS)
└─ LLM response (Sonnet):
   ├─ Input (context + query): ~2000 tokens → $0.006
   ├─ Output: ~500 tokens → $0.0075
   └─ Total: ~$0.014 per query
```

### Monthly Cost Estimates

| Team Size | Queries/Day | Documents | Est. Monthly Cost |
|-----------|-------------|-----------|-------------------|
| 5 people | 50 | 100 | $20-30 |
| 20 people | 200 | 500 | $80-120 |
| 50 people | 500 | 2000 | $200-350 |

### Optimization Tips

1. **Cache common queries** → Save ~50% on repeated questions
2. **Use Haiku for simple queries** → Save ~80% vs Sonnet
3. **Reduce context size** → Lower input token costs
4. **Batch embeddings** → Better rate limits
5. **Monitor via cost_logger** → Track and optimize

---

## 🎯 Evaluation Strategy

### 1. **Retrieval Quality**

```python
# Metrics we track:
- Precision@K: Are top-K results relevant?
- Recall: Did we find all relevant chunks?
- MRR (Mean Reciprocal Rank): Where's the first relevant result?

# Test set:
test_queries = [
    ("How do we deploy?", ["deploy.md", "cicd.md"]),
    ("What's our API rate limit?", ["api-docs.pdf"]),
    ...
]
```

### 2. **Response Quality**

```python
# Manual evaluation criteria:
evaluation = {
    "accuracy": "Is the answer factually correct?",
    "completeness": "Does it answer the full question?",
    "citations": "Are sources properly cited?",
    "relevance": "Is it focused on the question?",
    "clarity": "Is it easy to understand?"
}

# Scale: 1-5 for each criterion
```

### 3. **A/B Testing Prompts**

```python
# Compare prompt versions:
results = evaluate_prompts(
    versions=["v1.1", "v1.2"],
    test_queries=test_set,
    metrics=["accuracy", "citations", "latency"]
)
```

### 4. **User Feedback Loop**

```typescript
// Thumbs up/down on each response
<FeedbackButtons 
  onFeedback={(rating, comment) => {
    logFeedback(messageId, rating, comment);
  }}
/>
```

---

## 🚧 What We'd Improve in V2

### High Priority

1. **Hybrid Search**
   - Combine vector search (semantic) + keyword search (BM25)
   - Better for exact term matching (e.g., error codes, APIs)
   - Implementation: Use Chroma or implement custom

2. **Query Expansion**
   ```python
   original_query = "How to deploy?"
   expanded_queries = [
       "deployment process",
       "CI/CD pipeline",
       "production release steps"
   ]
   # Retrieve for all, merge results
   ```

3. **Semantic Caching**
   ```python
   # Cache responses for similar (not just identical) queries
   if similarity(new_query, cached_query) > 0.9:
       return cached_response
   ```

4. **Multi-Document Reasoning**
   - Current: Answers from individual chunks
   - V2: Compare/synthesize across multiple documents
   - Use case: "Compare our API docs vs implementation"

5. **Auto-Summarization on Upload**
   - Generate document summaries during indexing
   - Use for quick overview responses
   - Better context for clarification prompts

### Medium Priority

6. **Fine-Tuned Embeddings**
   - Train on company-specific terminology
   - Better retrieval for domain jargon
   - Requires: 1000+ query-doc pairs

7. **User Roles & Permissions**
   - Document-level access control
   - Filter results by user permissions
   - Essential for sensitive data

8. **Conversation Branching**
   - Save/share conversation threads
   - Fork conversations for "what-if" scenarios
   - Git-like interface for knowledge exploration

9. **Proactive Suggestions**
   ```python
   # Suggest related docs while typing
   as_user_types("How to depl..."):
       suggest(["Deployment Guide", "CI/CD Setup"])
   ```

10. **Multi-Modal Support**
    - Extract tables from PDFs properly
    - Support diagrams and images
    - Code block handling with syntax awareness

### Low Priority (Nice to Have)

11. **Graph-Based Context**
    - Link related documents
    - Knowledge graph for concepts
    - Navigate like a mind map

12. **Voice Interface**
    - Ask questions via voice
    - Useful for mobile, accessibility

13. **Slack/Teams Integration**
    - `/ask [question]` command
    - Bot in channels
    - Background document sync

---

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Integration tests
python tests/integration_test.py
```

### Test Coverage

```
backend/
├── test_rag_engine.py      # Chunking, retrieval, embeddings
├── test_prompt_manager.py  # Prompt construction, versioning
├── test_cost_logger.py     # Cost tracking, analytics
└── test_api.py             # Endpoint integration
```

---

## 📝 API Documentation

### POST `/upload`

Upload a document for indexing.

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"

# Response:
{
  "document_id": "abc123...",
  "filename": "document.pdf",
  "chunks_created": 47,
  "status": "success"
}
```

### POST `/chat`

Send a message and get a response.

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "How do we deploy?"}
    ],
    "model": "claude-sonnet-4",
    "stream": false
  }'

# Response:
{
  "response": "Based on deploy.md...",
  "sources": ["deploy.md", "cicd.md"],
  "confidence": 0.87,
  "metadata": {
    "model": "claude-sonnet-4",
    "chunks_used": 3
  }
}
```

### GET `/stats`

Get usage statistics.

```bash
curl "http://localhost:8000/stats"

# Response:
{
  "total_requests": 1247,
  "total_cost": 18.43,
  "avg_latency": 1.8,
  "documents_indexed": 52
}
```

---

## 🔒 Security Considerations

1. **API Keys**: Store in environment variables, never commit
2. **Input Validation**: Sanitize file uploads, check file types
3. **Rate Limiting**: Prevent abuse (implement in production)
4. **Access Control**: Add auth for production deployment
5. **Data Privacy**: Consider PII in documents, add redaction if needed

---

## 🤝 Contributing

We welcome contributions! Areas where help is needed:

- [ ] Implement Chroma/Pinecone adapters
- [ ] Add LLM provider abstraction (easy model switching)
- [ ] Build evaluation dashboard
- [ ] Improve chunking strategies
- [ ] Add export functionality (conversations, insights)

See `CONTRIBUTING.md` for guidelines.

---

## 📚 Resources

### RAG Deep Dives
- [Building RAG Systems (Anthropic)](https://www.anthropic.com/research/rag)
- [Vector Database Comparison](https://www.pinecone.io/learn/vector-database/)
- [Chunking Strategies](https://www.pinecone.io/learn/chunking-strategies/)

### Prompt Engineering
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Anthropic Prompt Library](https://docs.anthropic.com/prompts)

### Production Best Practices
- [LangChain Production Guide](https://python.langchain.com/docs/guides/productionization/)
- [RAG Evaluation Framework](https://docs.ragas.io/)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙋 FAQ

**Q: How many documents can it handle?**  
A: FAISS scales to ~100k documents in-memory. For more, use Pinecone or Chroma with disk persistence.

**Q: Can I use GPT-4 instead of Claude?**  
A: Yes! Update the model parameter in chat requests. The backend supports both.

**Q: How do I reduce costs?**  
A: Use Haiku for simple queries, cache common responses, reduce chunk overlap, or use smaller embeddings.

**Q: Is conversation history persisted?**  
A: Not by default. Add a database (PostgreSQL, MongoDB) to store conversations.

**Q: Can it handle code files?**  
A: Yes, but chunking code requires special handling. See `code_chunker.py` branch for specialized implementation.

---

Built with ❤️ for teams who deserve better than Ctrl+F

**Questions?** Open an issue or reach out!