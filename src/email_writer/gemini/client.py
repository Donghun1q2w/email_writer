from google import genai
from google.genai import types

from email_writer.config import Settings
from email_writer.core.prompt_builder import PromptBuilder


class GeminiClient:
    """Gemini API 호출을 담당하는 클라이언트"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate_with_file_search(self, prompt: str) -> str:
        """File Search를 활용한 이메일 생성 (동기 호출)

        google-genai SDK의 client.models.generate_content()는 동기 메서드.
        FastAPI가 threadpool에서 동기 함수를 실행하므로 동기 호출로 충분함.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=PromptBuilder.SYSTEM_INSTRUCTION,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[
                                self.settings.file_search_store_name
                            ]
                        )
                    )
                ],
                temperature=0.7,
            ),
        )

        return response.text
