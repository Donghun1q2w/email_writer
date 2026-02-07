from pydantic import BaseModel, Field


class GenerateEmailResponse(BaseModel):
    """Python 서버에서 VBA로 반환하는 응답"""

    success: bool = Field(description="요청 처리 성공 여부")
    generated_text: str = Field(
        default="",
        description="생성된 이메일 텍스트 (블록 대체용)"
    )
    error_message: str | None = Field(
        default=None,
        description="에러 발생 시 메시지"
    )
