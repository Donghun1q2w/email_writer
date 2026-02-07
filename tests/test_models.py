from datetime import datetime

import pytest

from email_writer.models.email_metadata import EmailMetadata
from email_writer.models.request import GenerateEmailRequest
from email_writer.models.response import GenerateEmailResponse


class TestGenerateEmailRequest:
    """GenerateEmailRequest 모델 테스트"""

    def test_with_all_fields(self):
        """모든 필드가 있을 때 직렬화/역직렬화"""
        data = {
            "full_body": "<html><body>전체 본문</body></html>",
            "selected_text": "선택된 텍스트",
            "to_recipients": "test@example.com",
            "subject": "테스트 제목",
            "is_reply": True,
            "additional_prompt": "추가 지시사항",
        }
        request = GenerateEmailRequest(**data)

        assert request.full_body == data["full_body"]
        assert request.selected_text == data["selected_text"]
        assert request.to_recipients == data["to_recipients"]
        assert request.subject == data["subject"]
        assert request.is_reply is True
        assert request.additional_prompt == data["additional_prompt"]

        # JSON 직렬화/역직렬화
        json_str = request.model_dump_json()
        restored = GenerateEmailRequest.model_validate_json(json_str)
        assert restored.full_body == request.full_body
        assert restored.is_reply == request.is_reply

    def test_with_defaults_only(self):
        """필수 필드만 있을 때 (나머지는 기본값)"""
        request = GenerateEmailRequest(
            full_body="<p>본문</p>",
            selected_text="키워드"
        )

        assert request.full_body == "<p>본문</p>"
        assert request.selected_text == "키워드"
        assert request.to_recipients == ""
        assert request.subject == ""
        assert request.is_reply is False
        assert request.additional_prompt == ""


class TestGenerateEmailResponse:
    """GenerateEmailResponse 모델 테스트"""

    def test_success_response(self):
        """성공 응답 직렬화/역직렬화"""
        response = GenerateEmailResponse(
            success=True,
            generated_text="생성된 이메일 본문입니다.",
            error_message=None,
        )

        assert response.success is True
        assert response.generated_text == "생성된 이메일 본문입니다."
        assert response.error_message is None

        # JSON 직렬화/역직렬화
        json_str = response.model_dump_json()
        restored = GenerateEmailResponse.model_validate_json(json_str)
        assert restored.success is True
        assert restored.generated_text == response.generated_text

    def test_error_response(self):
        """에러 응답 직렬화/역직렬화"""
        response = GenerateEmailResponse(
            success=False,
            generated_text="",
            error_message="API 호출 실패",
        )

        assert response.success is False
        assert response.generated_text == ""
        assert response.error_message == "API 호출 실패"

        # JSON 직렬화/역직렬화
        json_str = response.model_dump_json()
        restored = GenerateEmailResponse.model_validate_json(json_str)
        assert restored.success is False
        assert restored.error_message == "API 호출 실패"


class TestEmailMetadata:
    """EmailMetadata 모델 테스트"""

    def test_with_all_fields(self):
        """모든 필드가 있을 때 직렬화/역직렬화"""
        now = datetime(2025, 1, 15, 10, 30, 0)
        metadata = EmailMetadata(
            file_name="email_001.msg",
            subject="프로젝트 진행 상황 공유",
            sender="sender@example.com",
            recipients="recipient@example.com",
            date=now,
            is_reply=True,
            has_attachments=True,
            markdown_path="./data/converted_md/email_001.md",
        )

        assert metadata.file_name == "email_001.msg"
        assert metadata.subject == "프로젝트 진행 상황 공유"
        assert metadata.sender == "sender@example.com"
        assert metadata.recipients == "recipient@example.com"
        assert metadata.date == now
        assert metadata.is_reply is True
        assert metadata.has_attachments is True
        assert metadata.markdown_path == "./data/converted_md/email_001.md"

        # JSON 직렬화/역직렬화
        json_str = metadata.model_dump_json()
        restored = EmailMetadata.model_validate_json(json_str)
        assert restored.file_name == metadata.file_name
        assert restored.date == metadata.date

    def test_with_optional_fields_as_none(self):
        """선택 필드가 None일 때"""
        metadata = EmailMetadata(
            file_name="email_002.msg",
            subject="안녕하세요",
            sender="me@example.com",
            recipients="you@example.com",
            date=None,
            is_reply=False,
            has_attachments=False,
            markdown_path="./data/email_002.md",
        )

        assert metadata.date is None
        assert metadata.is_reply is False
        assert metadata.has_attachments is False

        # JSON 직렬화/역직렬화
        json_str = metadata.model_dump_json()
        restored = EmailMetadata.model_validate_json(json_str)
        assert restored.date is None
        assert restored.is_reply is False
