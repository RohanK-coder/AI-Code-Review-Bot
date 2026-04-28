import json
from typing import Any

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiClient:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError('Missing GEMINI_API_KEY')
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def embed_text(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=text,
        )
        embedding = response.embeddings[0].values
        return list(embedding)

    def generate_structured_review(self, prompt: str) -> dict[str, Any]:
        schema = {
            'type': 'OBJECT',
            'properties': {
                'summary': {'type': 'STRING'},
                'verdict': {'type': 'STRING', 'enum': ['approve', 'comment', 'request_changes']},
                'confidence': {'type': 'NUMBER'},
                'memory_used': {'type': 'BOOLEAN'},
                'comments': {
                    'type': 'ARRAY',
                    'items': {
                        'type': 'OBJECT',
                        'properties': {
                            'path': {'type': 'STRING'},
                            'line': {'type': 'INTEGER'},
                            'severity': {'type': 'STRING', 'enum': ['low', 'medium', 'high']},
                            'category': {
                                'type': 'STRING',
                                'enum': ['bug', 'security', 'performance', 'readability', 'test', 'design'],
                            },
                            'title': {'type': 'STRING'},
                            'body': {'type': 'STRING'},
                            'suggestion': {'type': 'STRING'},
                        },
                        'required': ['path', 'line', 'severity', 'category', 'title', 'body'],
                    },
                },
            },
            'required': ['summary', 'verdict', 'confidence', 'memory_used', 'comments'],
        }
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=schema,
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
