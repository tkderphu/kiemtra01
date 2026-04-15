from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from retriever import find_relevant_products, search_faq
from chain import get_answer

app = FastAPI(title="Chatbot Service", version="1.0")

class ChatRequest(BaseModel):
    user_id: int
    message: str
    conversation_history: list = []

@app.post('/chat')
async def chat(payload: ChatRequest):
    user_profile = {}
    try:
        # STEP 0: Get user behavior profile
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://ai_behavior:8001/analyze',
                json={'user_id': str(payload.user_id), 'session_id': 'temp'}
            ) as resp:
                if resp.status == 200:
                    user_profile = await resp.json()
    except Exception as e:
        print(f"Warning: Could not connect to behavior service: {e}")
        # Proceed with empty profile

    # STEP 1: Retrieval from multiple sources
    product_docs = find_relevant_products(payload.message, k=3)
    faq_docs = search_faq(payload.message, k=2)
    all_docs = product_docs + faq_docs
    
    # STEP 2: Generation
    reply = get_answer(
        user_question=payload.message,
        context_docs=all_docs,
        user_profile=user_profile,
        conversation_history=payload.conversation_history
    )
    
    # STEP 3: Extract sources for response
    sources = [
        {
            'product_id': doc.metadata.get('product_id'),
            'name': doc.metadata.get('name'),
            'price': doc.metadata.get('price')
        }
        for doc in product_docs
    ]
    
    return {
        'reply': reply,
        'sources': sources,
        'user_segment': user_profile.get('segment_name', 'unknown')
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
