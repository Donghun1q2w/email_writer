from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    # File Search Store
    file_search_store_name: str = ""

    # 서버
    server_host: str = "127.0.0.1"
    server_port: int = 8599

    # 변환
    msg_input_dir: str = "./data/msg_files"
    md_output_dir: str = "./data/converted_md"

    # 프롬프트 설정
    max_context_length: int = 8000
    default_language: str = "ko"

    model_config = {"env_file": ".env", "env_prefix": "EMAIL_WRITER_"}
