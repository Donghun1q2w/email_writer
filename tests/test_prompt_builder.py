import pytest

from email_writer.core.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """PromptBuilder 프롬프트 구성 테스트"""

    def test_build_new_email(self, settings):
        """새 이메일 작성용 프롬프트 생성"""
        builder = PromptBuilder(settings)
        prompt = builder.build(
            context_body="이전 메일 본문 내용",
            selected_text="미팅 일정 조율",
            subject="다음주 회의 일정",
            to_recipients="team@example.com",
            is_reply=False,
            additional_prompt="",
        )

        assert "다음 정보를 바탕으로 새 이메일을 작성하세요" in prompt
        assert "이전 메일 본문 내용" in prompt
        assert "미팅 일정 조율" in prompt
        assert "수신자: team@example.com" in prompt
        assert "제목: 다음주 회의 일정" in prompt
        assert "이전에 작성한 이메일들을 검색하여" in prompt

    def test_build_reply_email(self, settings):
        """회신 이메일 작성용 프롬프트 생성"""
        builder = PromptBuilder(settings)
        prompt = builder.build(
            context_body="원본 메일 내용입니다.",
            selected_text="확인했습니다. 진행하겠습니다.",
            subject="Re: 프로젝트 관련",
            to_recipients="sender@example.com",
            is_reply=True,
            additional_prompt="",
        )

        assert "다음은 회신할 원본 메일입니다" in prompt
        assert "이 맥락을 참고하여 회신을 작성하세요" in prompt
        assert "원본 메일 내용입니다." in prompt
        assert "확인했습니다. 진행하겠습니다." in prompt

    def test_build_with_additional_prompt(self, settings):
        """추가 지시사항이 있을 때"""
        builder = PromptBuilder(settings)
        prompt = builder.build(
            context_body="본문",
            selected_text="키워드",
            subject="",
            to_recipients="",
            is_reply=False,
            additional_prompt="격식있는 톤으로 작성해주세요",
        )

        assert "--- 추가 지시사항 ---" in prompt
        assert "격식있는 톤으로 작성해주세요" in prompt

    def test_build_truncates_long_body(self, settings):
        """긴 본문이 max_context_length로 잘리는지 확인"""
        builder = PromptBuilder(settings)
        long_body = "A" * (settings.max_context_length + 1000)

        prompt = builder.build(
            context_body=long_body,
            selected_text="요약 요청",
            subject="",
            to_recipients="",
            is_reply=False,
            additional_prompt="",
        )

        # 프롬프트 내의 본문 섹션은 max_context_length로 잘려야 함
        assert long_body[:settings.max_context_length] in prompt
        assert long_body in prompt  # 전체가 포함되면 안 됨
        # 잘린 버전은 포함됨
        assert len([line for line in prompt.split("\n") if "A" * 100 in line]) > 0

    def test_system_instruction_exists(self, settings):
        """SYSTEM_INSTRUCTION이 비어있지 않은지 확인"""
        builder = PromptBuilder(settings)
        assert len(builder.SYSTEM_INSTRUCTION) > 0
        assert "이메일 작성 도우미" in builder.SYSTEM_INSTRUCTION
        assert "File Search" in builder.SYSTEM_INSTRUCTION
