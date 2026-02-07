"""
MSG 파일 변환 + Gemini File Search Store 등록 CLI

사용법:
  python scripts/prepare_emails.py --msg-dir ./data/msg_files
  python scripts/prepare_emails.py --msg-dir ./data/msg_files --store-name "my-email-store"
"""
import argparse

from email_writer.config import Settings
from email_writer.converter.msg_to_markdown import MsgToMarkdownConverter
from email_writer.gemini.file_search import FileSearchManager


def main():
    parser = argparse.ArgumentParser(description="이메일 준비 도구")
    parser.add_argument("--msg-dir", required=True, help="MSG 파일 디렉토리")
    parser.add_argument(
        "--output-dir", default="./data/converted_md", help="변환 출력 디렉토리"
    )
    parser.add_argument(
        "--store-name", default=None, help="기존 File Search Store 이름 (없으면 새로 생성)"
    )
    args = parser.parse_args()

    settings = Settings()

    # 1. MSG -> Markdown 일괄 변환
    converter = MsgToMarkdownConverter(settings)
    metadata_list = converter.convert_batch(args.msg_dir, args.output_dir)
    print(f"변환 완료: {len(metadata_list)}개 파일")

    # 2. File Search Store 생성 또는 기존 사용
    fs_manager = FileSearchManager(settings)
    if args.store_name:
        store_name = args.store_name
    else:
        store_name = fs_manager.create_store("email-patterns")
        print(f"Store 생성: {store_name}")

    # 3. 변환된 파일 업로드
    for metadata in metadata_list:
        fs_manager.upload_markdown(store_name, metadata.markdown_path, metadata)
        print(f"업로드: {metadata.file_name}")

    # 4. Store 이름 안내
    print(f"\n완료! .env 파일에 다음을 추가하세요:")
    print(f"EMAIL_WRITER_FILE_SEARCH_STORE_NAME={store_name}")


if __name__ == "__main__":
    main()
