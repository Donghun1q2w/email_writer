import pytest

from email_writer.config import Settings


@pytest.fixture
def settings():
    """테스트용 Settings (실제 API 키 불필요한 테스트에서 사용)"""
    return Settings(
        gemini_api_key="test-api-key",
        gemini_model="gemini-2.5-flash",
        file_search_store_name="test-store",
        server_host="127.0.0.1",
        server_port=8599,
    )
