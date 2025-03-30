import uuid
import logging
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, request, jsonify
from sentence_transformers import SentenceTransformer

from static.app.config import settings
from static.app.core.gemini import Gemini
from static.app.core.qdrant import QdrantClient

ask_question_bp = Blueprint('ask_question', __name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_prompt(contexts, history, user_question):
    context_str = "\n\n".join(contexts)
    history_str = "\n\n".join(history)
    return (
        f"Your job is to produce final meeting minutes.\n\n"
        f"Existing meeting minutes:\n{context_str}\n\n"
        f"User has previously asked:\n{history_str}\n\n"
        "Please answer in the language that the question is written in.\n\n"
        "We have the opportunity to refine the meeting minutes using some additional context provided below.\n\n"
        f"User question:\n{user_question}\n\n"
    )


def retrieve_contexts(collection_name, query_vector):

    try:
        query_result = QdrantClient.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            score_threshold=0.3,
            with_payload=True,
        )
    except Exception as e:
        logger.error("Error retrieving contexts from Qdrant: %s", e)
        return []

    return [result.payload.get('text') for result in query_result if result.payload.get('text')]

def retrieve_history(collection_name, query_vector):
    try:
        query_result = QdrantClient.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            score_threshold=0.3,
            with_payload=True,
        )
    except Exception as e:
        logger.error("Error retrieving history from Qdrant: %s", e)
        return []

    return [result.payload.get('history') for result in query_result if result.payload.get('history')]


def get_response(prompt, user_question):

    try:
        client = Gemini.connect()
        response = Gemini.get_response(client, prompt, user_question)
    except Exception as e:
        logger.error("Error getting response from Gemini: %s", e)
        response = ""
    return response


def upsert_question(collection_name, user_question, question_vector):
    question_point = {
        "id": str(uuid.uuid4()),
        "vector": question_vector,
        "payload": {"history": user_question}
    }
    try:
        QdrantClient.upsert(collection_name, question_point)
    except Exception as e:
        logger.error("Error upserting question to Qdrant: %s", e)


def summarize_prompt(contexts):
    context_str = "\n\n".join(contexts)
    return (
        f"Your job is to produce a final meeting minutes\n"
        f"We have provided an existing meeting minutes up to a certain point:\n"
        f"We have the opportunity to refine the existing meeting minutes (only if needed) with some more context below.\n"
        f"------------\n"
        f"{context_str}\n"
        f"------------\n"
        f"Given the new context, refine the original meeting minutes within 500 words: following the format\n"
        f"Participants: <participants>\n"
        f"Discussed: <Discussed-items>\n"
        f"Follow-up actions: <a-list-of-follow-up-actions-with-owner-names>\n"
        f"If the context isn't useful, return the original meeting minutes. Highlight agreements and follow-up actions and owners.\n"
    )


@ask_question_bp.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json(silent=True)
    collection_name = data.get('collection')

    question_vector = model.encode("summarize meeting minutes")

    query_result = QdrantClient.search(
        collection_name=collection_name,
        query_vector=question_vector,
        limit=1000,
        score_threshold=0,
        with_payload=True,
    )

    prompt = summarize_prompt([result.payload.get('text') for result in query_result if result.payload.get('text')])

    answer = get_response(prompt, "Summarize meeting minutes")

    if not answer:
        return jsonify({"response": "No answer found"})

    return jsonify({"response": answer})

    if not answer:
        return jsonify({"response": "No answer found"})

    return jsonify({"response": answer})


@ask_question_bp.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json(silent=True)
    user_question = data.get('question') if data else None
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    collection_name = data.get('collection')

    try:
        question_vector = model.encode(user_question)
    except Exception as e:
        logger.error("Error encoding question: %s", e)
        return jsonify({"error": "Encoding error"}), 500

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(upsert_question, collection_name, user_question, question_vector)

    contexts = retrieve_contexts(collection_name, question_vector)
    history = retrieve_history(collection_name, question_vector)
    prompt = build_prompt(contexts, history, user_question)

    answer = get_response(prompt, user_question)

    if not answer:
        return jsonify({"response": "No answer found"})

    return jsonify({"response": answer})
