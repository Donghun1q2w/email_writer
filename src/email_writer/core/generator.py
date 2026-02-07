from bs4 import BeautifulSoup

from email_writer.config import Settings
from email_writer.core.prompt_builder import PromptBuilder
from email_writer.gemini.client import GeminiClient
from email_writer.models.request import GenerateEmailRequest


class EmailGenerator:
    """이메일 생성의 전체 흐름을 오케스트레이션"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.gemini_client = GeminiClient(settings)
        self.prompt_builder = PromptBuilder(settings)

    def generate(self, request: GenerateEmailRequest) -> str:
        """이메일 생성 메인 흐름 (동기).

        1. HTML 본문을 플레인 텍스트로 변환
        2. 프롬프트 구성
        3. Gemini API 호출 (File Search 포함)
        4. 생성된 텍스트 반환
        """
        plain_body = self._html_to_text(request.full_body)

        prompt = self.prompt_builder.build(
            context_body=plain_body,
            selected_text=request.selected_text,
            subject=request.subject,
            to_recipients=request.to_recipients,
            is_reply=request.is_reply,
            additional_prompt=request.additional_prompt,
        )

        generated = self.gemini_client.generate_with_file_search(prompt)
        return generated

    def _html_to_text(self, html: str) -> str:
        """HTML 메일 본문을 플레인 텍스트로 변환.

        BeautifulSoup을 사용하여 HTML 태그를 제거하고 텍스트만 추출.
        Outlook HTML 메일에는 style, head 등 불필요한 요소가 많으므로
        이를 제거하여 프롬프트 토큰을 절약한다.
        """
        if not html or not html.strip():
            return ""

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)

        return text
