"""
로컬 API 서버 시작

사용법:
  python scripts/start_server.py
"""
import uvicorn

from email_writer.config import Settings


def main():
    settings = Settings()
    uvicorn.run(
        "email_writer.server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
