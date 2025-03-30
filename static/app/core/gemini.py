from google import genai as gemini
from ..config import settings
from google.genai import types

class Gemini:

    @staticmethod
    def connect():
        client = gemini.Client(api_key=settings.GEMINI_API_KEY)
        return client

    @staticmethod
    def get_embedding(client, question):
        result = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=question,
            config = types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        return result.embeddings[0].values

    @staticmethod
    def get_response(client, system_text, user_question):
        system_part = types.Part.from_text(text=system_text)
        user_part = types.Part.from_text(text=user_question)
        system_content = types.UserContent(parts=[system_part])
        user_content = types.UserContent(parts=[user_part])
        contents = [system_content, user_content]
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents
        )
        return response.text
