import json
import os
from langchain.schema import Document
# Use HuggingFace embeddings or Mock instead of GenAI if no key is provided, for robust local running
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    pass
from langchain_community.vectorstores import Chroma

# A mock embeddings class to bypass real api call if GOOGLE_API_KEY isn't available
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

def load_products_from_json(path='data/products.json'):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    documents = []
    for product in products:
        content = f"""
        Tên: {product['name']}
        Giá: {product['price']:,}đ
        Danh mục: {product['category']}
        Mô tả: {product['description']}
        Công dụng: {', '.join(product.get('use_cases', []))}
        """
        metadata = {
            'product_id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'category': product['category']
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def build_knowledge_base(persist_dir='/data/chroma'):
    docs = load_products_from_json()
    if not docs:
        print("No products found to embed.")
        return None
        
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectorstore

if __name__ == '__main__':
    print("Building Knowledge Base...")
    build_knowledge_base('./chroma_local')
    print("KB Build complete.")
