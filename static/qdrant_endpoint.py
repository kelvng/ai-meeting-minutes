import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import time
from docx import Document
from flask import Blueprint, request, jsonify, current_app

from static.app.config import settings
from static.app.core.qdrant import QdrantClient
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

upload_file_bp = Blueprint('data', __name__)

class PointsList(BaseModel):
    id: str
    vector: list
    payload: dict

def upload_data(filename, texts):

    model = SentenceTransformer('all-MiniLM-L6-v2')

    chunk_size = 100
    all_chunks = []
    for i in range(0, len(texts), chunk_size):
        chunk = " | ".join(texts[i:i + chunk_size])
        all_chunks.append(chunk)
        print(chunk)

    for text in all_chunks:
        backoff = 1
        max_retries = 5
        success = False

        for attempt in range(max_retries):
            try:
                vector = model.encode(text)

                point = PointsList(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={'text': text}
                ).dict()

                print(QdrantClient.upsert(filename, point))

                success = True
                break
            except Exception as e:
                print(f"Error encountered: {e}. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2

        if not success:
            print(f"Skipping text after {max_retries} attempts: {text}")

    return {"success": True}


def process_file(filename, file_path):
    document = Document(file_path)
    texts = [para.text.strip() for para in document.paragraphs if para.text.strip()]

    upload_data(filename, texts)

    os.remove(file_path)

@upload_file_bp.route('/upload_file', methods=['POST'])
def upload_file():
    files_to_process = current_app.config['filesToProcess']
    file = request.files['file']
    file_path = os.path.join('data', file.filename)
    file.save(file_path)
    files_to_process.append(file_path)

    collection = request.form.get('collection')

    QdrantClient.create_collection(collection, 384, distance='Cosine')

    with ThreadPoolExecutor() as executor:
        for file_path in files_to_process:
            executor.submit(process_file, collection, file_path)

    return jsonify({"message": "File uploaded and processed successfully."})


@upload_file_bp.route('/create_thread', methods=['POST'])
def create_thread():
    data = request.get_json(silent=True)
    collection = data.get('collection')

    if not collection:
        return jsonify({"error": "No collection provided"}), 400

    try:
        QdrantClient.create_collection(collection, 384, distance='Cosine')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Thread created successfully."})




