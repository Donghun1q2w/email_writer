# Email Writer

사용자가 작성한 이메일들을 참고하여 유사한 톤과 구조로 이메일을 작성해주는 도구.

## 개요
- Windows 10 + Outlook 2013~2016 환경
- VBA (Outlook 연동) + Python (FastAPI 백엔드) + Google Gemini API (File Search)
- 기존 이메일 패턴을 Gemini File Search로 검색하여 톤/문체 유지

## 아키텍처
```
Outlook VBA  --HTTP-->  Python FastAPI  --API-->  Google Gemini (File Search)
```
- VBA: 메일 본문/블록 선택 캡처, Python 서버와 HTTP 통신, 생성 텍스트로 블록 대체
- Python: FastAPI 서버, 프롬프트 구성, Gemini API 호출
- Gemini: File Search Store에서 기존 이메일 패턴 검색, 이메일 생성

## 설치

### Python 환경
```bash
pip install -e .
# 또는
pip install -e ".[dev]"
```

### 환경변수 설정
```bash
cp .env.example .env
# .env 파일에서 GEMINI_API_KEY 등 설정
```

### Outlook VBA 매크로
outlook_addin/INSTALL.md 참조

## 사용법

### 1. 이메일 준비 (최초 1회)
```bash
python scripts/prepare_emails.py --msg-dir ./data/msg_files
```

### 2. 서버 시작
```bash
python scripts/start_server.py
```

### 3. Outlook에서 사용
1. 메일 작성/회신 창에서 요지/키워드를 입력하고 블록 선택
2. 매크로 실행 (Alt+F8 > GenerateEmail)
3. 추가 지시사항 입력 (선택)
4. 생성된 텍스트가 선택 영역을 대체

### Store 관리
```bash
python scripts/manage_store.py list-stores
python scripts/manage_store.py list-docs --store <store_name>
```

## 개발

### 테스트
```bash
pytest
```

### 린트
```bash
ruff check src/ tests/
```

## 프로젝트 구조
Brief overview: src/email_writer/ (server, core/, gemini/, converter/, models/), scripts/, tests/, outlook_addin/

## 라이선스
LICENSE 파일 참조
