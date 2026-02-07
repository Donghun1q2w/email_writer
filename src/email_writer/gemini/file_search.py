import time

from google import genai

from email_writer.config import Settings
from email_writer.models.email_metadata import EmailMetadata


class FileSearchManager:
    """Gemini File Search Store 생성/관리"""

    def __init__(self, settings: Settings):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.settings = settings

    def create_store(self, display_name: str = "email-patterns") -> str:
        """새 File Search Store 생성, store name 반환"""
        store = self.client.file_search_stores.create(
            config={"display_name": display_name}
        )
        return store.name

    def upload_markdown(
        self,
        store_name: str,
        md_file_path: str,
        metadata: EmailMetadata,
        poll_interval: float = 2.0,
        max_wait: float = 120.0,
    ) -> None:
        """마크다운 파일을 File Search Store에 업로드.

        google-genai SDK의 upload_to_file_search_store()를 사용하여
        파일 업로드와 Store 등록을 단일 호출로 수행한다.
        LongRunningOperation을 반환하므로 완료까지 폴링한다.

        Args:
            store_name: File Search Store 리소스 이름
            md_file_path: 업로드할 마크다운 파일 경로
            metadata: 이메일 메타데이터
            poll_interval: 폴링 간격 (초, 기본 2초)
            max_wait: 최대 대기 시간 (초, 기본 120초)

        Raises:
            TimeoutError: max_wait 초과 시
            Exception: 업로드 실패 시
        """
        custom_metadata = [
            {"key": "subject", "string_value": metadata.subject},
            {"key": "sender", "string_value": metadata.sender},
            {"key": "recipients", "string_value": metadata.recipients},
            {"key": "is_reply", "string_value": str(metadata.is_reply)},
        ]

        if metadata.date:
            custom_metadata.append(
                {"key": "date", "string_value": metadata.date.isoformat()}
            )

        operation = self.client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=store_name,
            file=md_file_path,
            config={
                "display_name": metadata.file_name,
                "custom_metadata": custom_metadata,
            },
        )

        elapsed = 0.0
        while not operation.done:
            if elapsed >= max_wait:
                raise TimeoutError(
                    f"파일 업로드 타임아웃 ({max_wait}초 초과): {metadata.file_name}"
                )
            time.sleep(poll_interval)
            elapsed += poll_interval

        if operation.error:
            raise Exception(
                f"파일 업로드 실패: {metadata.file_name} - {operation.error}"
            )

    def list_stores(self):
        """전체 File Search Store 목록 조회"""
        return self.client.file_search_stores.list()

    def list_documents(self, store_name: str):
        """Store 내 문서 목록 조회"""
        return self.client.file_search_stores.documents.list(
            file_search_store_name=store_name
        )

    def delete_document(self, store_name: str, document_name: str):
        """Store에서 문서 삭제"""
        self.client.file_search_stores.documents.delete(
            file_search_store_name=store_name,
            name=document_name,
        )

    def delete_store(self, store_name: str):
        """File Search Store 삭제"""
        self.client.file_search_stores.delete(name=store_name)
