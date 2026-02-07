from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI TestClient with mocked Settings and EmailGenerator"""
    with patch("email_writer.server.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-2.5-flash"
        mock_settings.file_search_store_name = "test-store"
        mock_settings.server_host = "127.0.0.1"
        mock_settings.server_port = 8599
        mock_settings.max_context_length = 8000
        mock_settings.default_language = "ko"

        with patch("email_writer.server.EmailGenerator") as MockGenerator:
            mock_gen = MockGenerator.return_value
            mock_gen.generate = MagicMock(return_value="생성된 이메일 본문입니다.")

            from email_writer.server import app
            yield TestClient(app), mock_gen


def test_health_check(client):
    """GET /api/health 헬스체크 테스트"""
    test_client, _ = client
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_email_success(client):
    """POST /api/generate-email 성공 케이스"""
    test_client, mock_gen = client
    mock_gen.generate.return_value = "안녕하세요, 회의 일정 확인 부탁드립니다."

    response = test_client.post(
        "/api/generate-email",
        json={
            "full_body": "<html><body>원본 메일</body></html>",
            "selected_text": "회의 일정 확인 요청",
            "subject": "RE: 회의 일정",
            "is_reply": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["generated_text"] == "안녕하세요, 회의 일정 확인 부탁드립니다."
    assert data["error_message"] is None


def test_generate_email_error(client):
    """POST /api/generate-email 에러 케이스"""
    test_client, mock_gen = client
    mock_gen.generate.side_effect = Exception("API 호출 실패")

    response = test_client.post(
        "/api/generate-email",
        json={
            "full_body": "<html><body>테스트</body></html>",
            "selected_text": "테스트 키워드",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "API 호출 실패" in data["error_message"]


def test_generate_email_validation_error(client):
    """POST /api/generate-email 필수 필드 누락"""
    test_client, _ = client

    response = test_client.post(
        "/api/generate-email",
        json={"full_body": "테스트"},  # selected_text 누락
    )

    assert response.status_code == 422


def test_generate_email_minimal_request(client):
    """POST /api/generate-email 최소 필드만 제공"""
    test_client, mock_gen = client
    mock_gen.generate.return_value = "생성된 응답입니다."

    response = test_client.post(
        "/api/generate-email",
        json={
            "full_body": "<html><body>본문</body></html>",
            "selected_text": "키워드",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["generated_text"] == "생성된 응답입니다."
