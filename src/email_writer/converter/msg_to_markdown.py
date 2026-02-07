from pathlib import Path

import extract_msg
from markitdown import MarkItDown

from email_writer.config import Settings
from email_writer.models.email_metadata import EmailMetadata


class MsgToMarkdownConverter:
    """MSG 파일을 Markdown으로 변환"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.converter = MarkItDown()

    def convert_single(self, msg_path: str, output_dir: str) -> EmailMetadata:
        """단일 MSG 파일 변환, 메타데이터 반환"""
        msg_file = Path(msg_path)

        result = self.converter.convert(str(msg_file))
        markdown_content = result.text_content

        metadata = self._extract_metadata(msg_file, markdown_content)

        md_filename = msg_file.stem + ".md"
        md_path = Path(output_dir) / md_filename
        md_path.write_text(markdown_content, encoding="utf-8")

        metadata.markdown_path = str(md_path)
        return metadata

    def convert_batch(self, input_dir: str, output_dir: str) -> list[EmailMetadata]:
        """디렉토리 내 모든 MSG 파일 일괄 변환"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []
        for msg_file in input_path.glob("*.msg"):
            try:
                metadata = self.convert_single(str(msg_file), str(output_path))
                results.append(metadata)
            except Exception as e:
                print(f"변환 실패: {msg_file.name} - {e}")

        return results

    def _extract_metadata(self, msg_file: Path, markdown_content: str) -> EmailMetadata:
        """MSG 파일에서 메타데이터 추출.

        extract-msg 라이브러리를 사용하여 .msg 파일의 구조화된 헤더 정보를 직접 읽는다.
        """
        msg = extract_msg.Message(str(msg_file))
        try:
            sender = msg.sender or ""
            recipients = msg.to or ""
            subject = msg.subject or ""
            date = msg.date

            is_reply = False
            if subject:
                upper_subject = subject.upper().strip()
                is_reply = (
                    upper_subject.startswith("RE:")
                    or subject.strip().startswith("답장:")
                    or subject.strip().startswith("회신:")
                )

            has_attachments = len(msg.attachments) > 0

            return EmailMetadata(
                file_name=msg_file.name,
                subject=subject,
                sender=sender,
                recipients=recipients,
                date=date,
                is_reply=is_reply,
                has_attachments=has_attachments,
                markdown_path="",
            )
        finally:
            msg.close()
