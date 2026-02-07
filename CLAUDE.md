# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Email Writer - Outlook 2013-2016에서 사용자의 기존 이메일 패턴을 참고하여 이메일을 자동 작성하는 도구.
VBA(Outlook) + Python(FastAPI) + Google Gemini API(File Search) 3-tier 아키텍처.

## Tech Stack

- Python 3.10+
- FastAPI (동기 엔드포인트, threadpool 실행)
- Google Gemini API (`google-genai` SDK) - File Search를 통한 RAG 기반 이메일 생성
- Pydantic v2 + pydantic-settings (데이터 모델 및 설정 관리)
- markitdown + extract-msg (MSG → Markdown 변환)
- BeautifulSoup4 (HTML → 텍스트 변환)
- VBA (Outlook 매크로, MSXML2.XMLHTTP.6.0으로 HTTP 통신)

## Build & Run

```bash
# 설치
pip install -e .
pip install -e ".[dev]"  # 개발 의존성 포함

# 서버 시작
python scripts/start_server.py

# 이메일 준비 (MSG → Markdown 변환 + File Search Store 등록)
python scripts/prepare_emails.py --msg-dir ./data/msg_files

# Store 관리
python scripts/manage_store.py list-stores
python scripts/manage_store.py create --name "my-store"
```

## Test & Lint

```bash
pytest                      # 전체 테스트
pytest tests/test_models.py # 단일 테스트 파일
ruff check src/ tests/      # 린트
ruff format src/ tests/     # 포맷
```

## Architecture

### Data Flow (Runtime)
```
Outlook VBA → HTTP POST (localhost:8599) → FastAPI server → Gemini API (File Search) → 생성된 텍스트 → VBA → 블록 대체
```

### Key Modules
- `src/email_writer/server.py` - FastAPI 앱, POST /api/generate-email, GET /api/health
- `src/email_writer/core/generator.py` - EmailGenerator: HTML→텍스트, 프롬프트 구성, Gemini 호출 오케스트레이션
- `src/email_writer/core/prompt_builder.py` - PromptBuilder: 새 메일/회신 프롬프트 구성, SYSTEM_INSTRUCTION 정의
- `src/email_writer/gemini/client.py` - GeminiClient: google-genai SDK 래퍼, File Search 통합 생성
- `src/email_writer/gemini/file_search.py` - FileSearchManager: Store CRUD, 파일 업로드 (LongRunningOperation 폴링)
- `src/email_writer/converter/msg_to_markdown.py` - MsgToMarkdownConverter: markitdown(본문) + extract-msg(메타데이터)
- `src/email_writer/models/` - Pydantic 모델 (request, response, email_metadata)
- `src/email_writer/config.py` - Settings (pydantic-settings, EMAIL_WRITER_ prefix 환경변수)
- `outlook_addin/EmailWriter.bas` - VBA 매크로 (메일 캡처, JSON 빌드, HTTP 전송, 응답 파싱, 블록 대체)

### Design Decisions
- 전체 동기 아키텍처: Gemini SDK가 동기 메서드이므로 FastAPI가 threadpool에서 실행
- VBA JSON 처리: 네이티브 JSON 파서 없이 InStr/Mid 기반 문자열 파싱 (고정 스키마)
- File Search Store: 사전 준비 단계에서 MSG→MD 변환 후 업로드, 런타임에 RAG 쿼리

## Configuration

환경변수 (`.env` 파일, `EMAIL_WRITER_` prefix):
- `EMAIL_WRITER_GEMINI_API_KEY` - Gemini API 키 (필수)
- `EMAIL_WRITER_FILE_SEARCH_STORE_NAME` - File Search Store 이름 (prepare_emails.py로 생성)
- `EMAIL_WRITER_SERVER_PORT` - 서버 포트 (기본 8599)
