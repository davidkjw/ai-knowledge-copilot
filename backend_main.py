# main.py - FastAPI Backend for Knowledge Copilot
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

from rag_engine import RAGEngine
from prompt_manager import PromptManager
from cost_logger import CostLogger

app = FastAPI(title="Knowledge Copilot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_engine = RAGEngine(
    embedding_model="text-embedding-ada-002",
    vector_db_type="faiss",  # or "chroma" or "pinecone"
    chunk_size=500,
    chunk_overlap=50
)

prompt_manager = PromptManager(version="v1.2.0")
cost_logger = CostLogger()


# Request/Response Models
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "claude-sonnet-4"
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    confidence: float
    metadata: Dict[str, Any]


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    status: str


# Endpoints
@app.get("/")
async def root():
    return {
        "service": "Knowledge Copilot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document for RAG"""
    try:
        # Read file content
        content = await file.read()
        
        # Process document based on type
        if file.filename.endswith('.pdf'):
            text = await rag_engine.extract_text_from_pdf(content)
        elif file.filename.endswith('.md'):
            text = content.decode('utf-8')
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Create chunks and embeddings
        doc_id = await rag_engine.add_document(
            text=text,
            metadata={"filename": file.filename, "uploaded_at": datetime.now().isoformat()}
        )
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            chunks_created=len(rag_engine.get_document_chunks(doc_id)),
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint with streaming support"""
    if request.stream:
        return StreamingResponse(
            stream_chat_response(request),
            media_type="text/event-stream"
        )
    else:
        return await generate_chat_response(request)


async def stream_chat_response(request: ChatRequest):
    """Stream chat responses token by token"""
    try:
        # Extract latest user message
        user_message = request.messages[-1].content
        conversation_history = request.messages[:-1]
        
        # Log request start
        request_id = cost_logger.start_request(
            model=request.model,
            input_text=user_message
        )
        
        # Retrieve relevant context
        retrieval_results = await rag_engine.retrieve(
            query=user_message,
            top_k=5,
            confidence_threshold=0.7
        )
        
        # Check if we have good enough context
        if not retrieval_results or retrieval_results[0]['score'] < 0.7:
            # Low confidence - ask clarifying question
            clarification = await prompt_manager.get_clarification_prompt(
                query=user_message,
                available_docs=rag_engine.list_documents()
            )
            
            async for chunk in stream_llm_response(clarification, request.model):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            cost_logger.end_request(request_id, output_text=clarification)
            return
        
        # Build context-enhanced prompt
        context = "\n\n".join([r['text'] for r in retrieval_results])
        
        # Check context size and summarize if needed
        if len(context) > 4000:  # Token estimation
            context = await summarize_context(context, request.model)
        
        # Get system prompt and construct final prompt
        system_prompt = prompt_manager.get_system_prompt()
        final_prompt = prompt_manager.construct_prompt(
            system=system_prompt,
            context=context,
            conversation_history=conversation_history,
            user_query=user_message
        )
        
        # Stream response from LLM
        full_response = ""
        async for chunk in stream_llm_response(final_prompt, request.model):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        # Send metadata
        metadata = {
            "sources": [r['metadata']['filename'] for r in retrieval_results],
            "confidence": retrieval_results[0]['score'],
            "model": request.model,
            "processing_time": cost_logger.get_request_time(request_id)
        }
        
        yield f"data: {json.dumps({'metadata': metadata})}\n\n"
        
        # Log cost
        cost_logger.end_request(request_id, output_text=full_response)
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def generate_chat_response(request: ChatRequest) -> ChatResponse:
    """Non-streaming chat response"""
    user_message = request.messages[-1].content
    conversation_history = request.messages[:-1]
    
    # Retrieve context
    retrieval_results = await rag_engine.retrieve(
        query=user_message,
        top_k=5,
        confidence_threshold=0.7
    )
    
    if not retrieval_results or retrieval_results[0]['score'] < 0.7:
        # Low confidence response
        response_text = f"I don't have enough context to answer that confidently. Could you provide more details or rephrase your question?"
        return ChatResponse(
            response=response_text,
            sources=[],
            confidence=0.0,
            metadata={"reason": "low_retrieval_confidence"}
        )
    
    # Build and execute prompt
    context = "\n\n".join([r['text'] for r in retrieval_results])
    system_prompt = prompt_manager.get_system_prompt()
    final_prompt = prompt_manager.construct_prompt(
        system=system_prompt,
        context=context,
        conversation_history=conversation_history,
        user_query=user_message
    )
    
    # Get LLM response
    response_text = await call_llm(final_prompt, request.model)
    
    return ChatResponse(
        response=response_text,
        sources=[r['metadata']['filename'] for r in retrieval_results],
        confidence=retrieval_results[0]['score'],
        metadata={
            "model": request.model,
            "chunks_used": len(retrieval_results)
        }
    )


@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return {"documents": rag_engine.list_documents()}


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its embeddings"""
    success = await rag_engine.delete_document(doc_id)
    if success:
        return {"status": "deleted", "document_id": doc_id}
    raise HTTPException(status_code=404, detail="Document not found")


@app.get("/stats")
async def get_stats():
    """Get usage statistics"""
    return {
        "total_requests": cost_logger.get_total_requests(),
        "total_cost": cost_logger.get_total_cost(),
        "avg_latency": cost_logger.get_avg_latency(),
        "documents_indexed": rag_engine.get_document_count()
    }


# Helper functions
async def stream_llm_response(prompt: str, model: str):
    """Stream tokens from LLM (mock implementation)"""
    # In production, this would call actual LLM API
    response = f"Based on the provided documentation, here's what I found: {prompt[:100]}..."
    
    for char in response:
        yield char
        await asyncio.sleep(0.01)


async def call_llm(prompt: str, model: str) -> str:
    """Non-streaming LLM call (mock implementation)"""
    return f"Response based on: {prompt[:200]}..."


async def summarize_context(context: str, model: str) -> str:
    """Summarize context if too large"""
    summary_prompt = f"Summarize the following context concisely:\n\n{context}"
    return await call_llm(summary_prompt, model)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)