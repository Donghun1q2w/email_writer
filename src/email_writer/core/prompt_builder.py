from email_writer.config import Settings


class PromptBuilder:
    """Gemini API 호출용 프롬프트를 구성"""

    SYSTEM_INSTRUCTION = """당신은 이메일 작성 도우미입니다.
사용자가 이전에 작성한 이메일들의 톤, 문체, 구조를 참고하여
자연스러운 이메일을 작성해주세요.

핵심 규칙:
1. File Search를 통해 검색된 기존 이메일들의 문체와 톤을 최대한 유지하세요.
2. 수신자와 상황에 맞는 적절한 인사말과 마무리를 사용하세요.
3. 한국어 비즈니스 이메일의 관례를 따르세요.
4. 간결하고 명확한 문장을 사용하세요.
5. 생성된 이메일 본문만 출력하세요 (제목, 설명, 마크다운 포맷 등 불필요).
6. 기존 이메일에서 자주 사용하는 표현, 인사말, 마무리 패턴을 적극 활용하세요."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def build(
        self,
        context_body: str,
        selected_text: str,
        subject: str,
        to_recipients: str,
        is_reply: bool,
        additional_prompt: str,
    ) -> str:
        """컨텍스트 기반 프롬프트 구성"""
        parts = []

        if is_reply:
            parts.append("다음은 회신할 원본 메일입니다. 이 맥락을 참고하여 회신을 작성하세요.")
        else:
            parts.append("다음 정보를 바탕으로 새 이메일을 작성하세요.")

        if context_body:
            truncated = context_body[: self.settings.max_context_length]
            parts.append(f"\n--- 메일 본문 (맥락) ---\n{truncated}")

        if to_recipients:
            parts.append(f"\n수신자: {to_recipients}")

        if subject:
            parts.append(f"제목: {subject}")

        parts.append(f"\n--- 작성 요지/키워드 ---\n{selected_text}")

        parts.append("\n이전에 작성한 이메일들을 검색하여 문체와 패턴을 참고하세요.")

        if additional_prompt:
            parts.append(f"\n--- 추가 지시사항 ---\n{additional_prompt}")

        return "\n".join(parts)
