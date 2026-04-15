from fastapi import FastAPI, HTTPException
import subprocess
import os
import json
import threading
from kafka import KafkaConsumer
from embedder import get_embeddings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

app = FastAPI(title="Knowledge Base Service", version="1.0")

def consume_kafka():
    kafka_broker = os.environ.get('KAFKA_BROKER', 'kafka:9092')
    try:
        consumer = KafkaConsumer(
            'product_updates',
            bootstrap_servers=kafka_broker,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print("Kafka consumer started listening to product_updates...")
        for message in consumer:
            product = message.value
            print(f"Consumed message: {product}")
            try:
                content = f"""
                Tên: {product.get('name', 'N/A')}
                Giá: {product.get('price', 0):,}đ
                Danh mục: {product.get('category', 'N/A')}
                Mô tả: {product.get('description', '')}
                Công dụng: {', '.join(product.get('use_cases', []))}
                """
                metadata = {
                    'product_id': product.get('id', 0),
                    'name': product.get('name', 'N/A'),
                    'price': product.get('price', 0),
                    'category': product.get('category', 'N/A')
                }
                doc = Document(page_content=content, metadata=metadata)
                embeddings = get_embeddings()
                vectorstore = Chroma(persist_directory='/data/chroma', embedding_function=embeddings)
                vectorstore.add_documents([doc])
                print(f"Successfully updated Chroma vectorstore for product {metadata['product_id']}")
            except Exception as e:
                print(f"Error indexing product into Chroma: {e}")
    except Exception as e:
        print(f"Kafka consumer could not start: {e}")

@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=consume_kafka, daemon=True)
    t.start()

@app.post("/rebuild")
def rebuild_kb():
    try:
        # Simplistic way to trigger rebuilding
        subprocess.run(["python", "embedder.py"], check=True)
        return {"status": "success", "message": "Knowledge base rebuilt successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
