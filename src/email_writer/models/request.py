from pydantic import BaseModel, Field


class GenerateEmailRequest(BaseModel):
    """VBA에서 Python 서버로 전송하는 요청"""

    full_body: str = Field(
        description="메일 편집기의 전체 본문 (HTML). 맥락 파악에 사용"
    )
    selected_text: str = Field(
        description="사용자가 블록 선택한 텍스트. 수신자/요지/키워드 포함"
    )
    to_recipients: str = Field(
        default="",
        description="수신자 이메일 주소"
    )
    subject: str = Field(
        default="",
        description="메일 제목"
    )
    is_reply: bool = Field(
        default=False,
        description="회신 메일 여부"
    )
    additional_prompt: str = Field(
        default="",
        description="사용자 추가 지시사항"
    )
