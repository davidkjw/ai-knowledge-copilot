# AI Knowledge Copilot - Environment Configuration
# Copy this file to .env and fill in your values

# ============================================
# API Keys (REQUIRED)
# ============================================

# Anthropic API Key (for Claude models)
# Get yours at: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI API Key (for embeddings and optional GPT models)
# Get yours at: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# ============================================
# Vector Database Configuration
# ============================================

# Choose: "faiss", "chroma", or "pinecone"
VECTOR_DB_TYPE=faiss

# Pinecone Config (only if using Pinecone)
# PINECONE_API_KEY=your-pinecone-key
# PINECONE_ENVIRONMENT=us-west1-gcp
# PINECONE_INDEX_NAME=knowledge-copilot

# Chroma Config (only if using Chroma with client-server mode)
# CHROMA_HOST=localhost
# CHROMA_PORT=8001

# ============================================
# Model Configuration
# ============================================

# Default LLM model
DEFAULT_MODEL=claude-sonnet-4

# Embedding model
EMBEDDING_MODEL=text-embedding-ada-002

# Alternative: Use local embeddings (no API costs)
# EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ============================================
# RAG Configuration
# ============================================

# Chunk size for document splitting (characters)
CHUNK_SIZE=500

# Chunk overlap to preserve context
CHUNK_OVERLAP=50

# Number of chunks to retrieve per query
TOP_K=5

# Minimum confidence threshold (0.0-1.0)
CONFIDENCE_THRESHOLD=0.7

# Maximum context size before summarization (characters)
MAX_CONTEXT_SIZE=4000

# ============================================
# Application Settings
# ============================================

# Backend server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Environment: development, staging, production
ENVIRONMENT=development

# ============================================
# Storage Configuration
# ============================================

# Upload directory for documents
UPLOAD_DIR=./uploads

# Vector database persistence directory
VECTOR_DATA_DIR=./vector_data

# Log files directory
LOG_DIR=./logs

# ============================================
# Performance & Limits
# ============================================

# Max file upload size (MB)
MAX_UPLOAD_SIZE_MB=10

# Request timeout (seconds)
REQUEST_TIMEOUT=30

# Max tokens for LLM responses
MAX_OUTPUT_TOKENS=1000

# Enable streaming responses
ENABLE_STREAMING=true

# ============================================
# Monitoring & Logging
# ============================================

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Enable cost logging
ENABLE_COST_LOGGING=true

# Cost log file
COST_LOG_FILE=./logs/cost_logs.jsonl

# Enable performance metrics
ENABLE_METRICS=true

# ============================================
# Optional: Database (for conversation storage)
# ============================================

# PostgreSQL connection string (if using database)
# DATABASE_URL=postgresql://user:password@localhost:5432/copilot

# ============================================
# Optional: Redis (for caching)
# ============================================

# Redis connection string (if using Redis)
# REDIS_URL=redis://localhost:6379/0

# Cache TTL in seconds
# CACHE_TTL=3600

# ============================================
# Optional: Authentication
# ============================================

# Enable authentication (for production)
# ENABLE_AUTH=false

# JWT secret key (generate with: openssl rand -hex 32)
# JWT_SECRET=your-secret-key-here

# Token expiration (hours)
# TOKEN_EXPIRATION_HOURS=24

# ============================================
# Optional: Rate Limiting
# ============================================

# Enable rate limiting
# ENABLE_RATE_LIMITING=true

# Requests per minute per user
# RATE_LIMIT_PER_MINUTE=60

# ============================================
# Development Settings
# ============================================

# Enable debug mode (more verbose logging)
DEBUG=false

# Enable hot reload for development
HOT_RELOAD=true

# Enable CORS for all origins (dev only!)
CORS_ALLOW_ALL=true

# ============================================
# Evaluation & Testing
# ============================================

# Enable automatic evaluation
ENABLE_AUTO_EVAL=false

# Evaluation test set
EVAL_TEST_SET=retrieval_accuracy

# Prompt version for testing
PROMPT_VERSION=v1.2.0