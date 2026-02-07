from fastapi import FastAPI

from email_writer.config import Settings
from email_writer.core.generator import EmailGenerator
from email_writer.models.request import GenerateEmailRequest
from email_writer.models.response import GenerateEmailResponse

app = FastAPI(title="Email Writer API")
settings = Settings()
generator = EmailGenerator(settings)


@app.post("/api/generate-email", response_model=GenerateEmailResponse)
def generate_email(request: GenerateEmailRequest):
    """이메일 생성 엔드포인트 - VBA에서 호출

    동기 함수로 정의. FastAPI는 동기 엔드포인트를 자동으로
    threadpool executor에서 실행하므로 이벤트 루프를 블로킹하지 않음.
    """
    try:
        generated_text = generator.generate(request)
        return GenerateEmailResponse(
            success=True,
            generated_text=generated_text,
        )
    except Exception as e:
        return GenerateEmailResponse(
            success=False,
            error_message=str(e),
        )


@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
