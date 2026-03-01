import httpx
from ..config import DIFY_API_URL, DIFY_API_KEY
from typing import AsyncGenerator


class LLMService:
    def __init__(self):
        self.api_url = DIFY_API_URL
        self.api_key = DIFY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._is_loaded = bool(self.api_key)
    
    async def predict_gloss(self, text: str) -> tuple[str, float]:
        """
        Generate sign language gloss using Dify LLM API (blocking mode).
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/chat-messages",
                headers=self.headers,
                json={
                    "inputs": {},
                    "query": text,
                    "response_mode": "blocking",
                    "user": "api-user"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Dify API error: {response.text}")
            
            data = response.json()
            gloss = data.get("answer", "")
            confidence = 0
            
            return gloss, confidence
    
    async def predict_gloss_stream(self, text: str) -> AsyncGenerator[str, None]:
        """
        Generate sign language gloss using Dify LLM API (streaming mode).
        Yields text chunks as they arrive.
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.api_url}/chat-messages",
                headers=self.headers,
                json={
                    "inputs": {},
                    "query": text,
                    "response_mode": "streaming",
                    "user": "api-user"
                },
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    raise Exception(f"Dify API error: {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        import json
                        try:
                            data = json.loads(line[5:].strip())
                            if data.get("event") == "message":
                                answer = data.get("answer", "")
                                if answer:
                                    yield answer
                        except json.JSONDecodeError:
                            continue

    @property 
    def is_loaded(self) -> bool:
        return self._is_loaded


llm_service = LLMService()
