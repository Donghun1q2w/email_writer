from datetime import datetime

from pydantic import BaseModel


class EmailMetadata(BaseModel):
    """변환된 이메일의 메타데이터 (File Search 등록 시 사용)"""

    file_name: str
    subject: str
    sender: str
    recipients: str
    date: datetime | None = None
    is_reply: bool = False
    has_attachments: bool = False
    markdown_path: str
