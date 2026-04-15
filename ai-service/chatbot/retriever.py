from langchain_community.vectorstores import Chroma
import os

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    pass

class MockEmbeddings:
    def embed_documents(self, texts):
        return [[0.1]*384 for _ in texts]
    def embed_query(self, text):
        return [0.1]*384

def get_embeddings():
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        return GoogleGenerativeAIEmbeddings(
            model='models/embedding-001',
            google_api_key=api_key
        )
    return MockEmbeddings()

def get_vectorstore(persist_dir='/data/chroma'):
    embeddings = get_embeddings()
    # Check if empty, fallback gracefully.
    try:
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    except Exception:
        return None

def find_relevant_products(query, k=3):
    vectorstore = get_vectorstore()
    if not vectorstore:
        return []
    try:
        docs = vectorstore.similarity_search(query, k=k)
        return docs
    except Exception:
        return []

def search_faq(query, k=2):
    # In a full app, FAQs might have a separate collection
    vectorstore = get_vectorstore(persist_dir='/data/chroma')
    if not vectorstore:
        return []
    try:
        docs = vectorstore.similarity_search(query + " faq", k=k)
        return docs
    except Exception:
        return []
