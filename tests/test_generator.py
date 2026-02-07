import pytest

from email_writer.core.generator import EmailGenerator


class TestEmailGeneratorHtmlToText:
    """EmailGenerator._html_to_text 메서드 테스트"""

    def test_html_to_text_basic(self, settings):
        """기본 HTML을 텍스트로 변환"""
        generator = EmailGenerator(settings)
        html = """
        <html>
            <body>
                <p>안녕하세요.</p>
                <p>이메일 본문입니다.</p>
            </body>
        </html>
        """
        text = generator._html_to_text(html)

        assert "안녕하세요." in text
        assert "이메일 본문입니다." in text
        assert "<p>" not in text
        assert "<html>" not in text

    def test_html_to_text_removes_script_style(self, settings):
        """script, style 태그가 제거되는지 확인"""
        generator = EmailGenerator(settings)
        html = """
        <html>
            <head>
                <style>
                    body { color: red; }
                </style>
                <script>
                    console.log('test');
                </script>
            </head>
            <body>
                <p>실제 본문</p>
            </body>
        </html>
        """
        text = generator._html_to_text(html)

        assert "실제 본문" in text
        assert "color: red" not in text
        assert "console.log" not in text
        assert "<style>" not in text
        assert "<script>" not in text

    def test_html_to_text_empty_input(self, settings):
        """빈 입력에 대한 처리"""
        generator = EmailGenerator(settings)

        assert generator._html_to_text("") == ""
        assert generator._html_to_text("   ") == ""
        assert generator._html_to_text(None) == ""

    def test_html_to_text_outlook_html(self, settings):
        """Outlook 스타일 HTML 처리 (MsoNormal 클래스 등)"""
        generator = EmailGenerator(settings)
        outlook_html = """
        <html xmlns:v="urn:schemas-microsoft-com:vml"
              xmlns:o="urn:schemas-microsoft-com:office:office"
              xmlns:w="urn:schemas-microsoft-com:office:word"
              xmlns:m="http://schemas.microsoft.com/office/2004/12/omml">
        <head>
            <meta http-equiv=Content-Type content="text/html; charset=utf-8">
            <style>
                .MsoNormal { font-family: 'Calibri'; }
            </style>
        </head>
        <body lang=KO>
            <div class="WordSection1">
                <p class="MsoNormal">안녕하세요,</p>
                <p class="MsoNormal">업무 관련 문의드립니다.</p>
                <p class="MsoNormal">감사합니다.</p>
            </div>
        </body>
        </html>
        """
        text = generator._html_to_text(outlook_html)

        assert "안녕하세요," in text
        assert "업무 관련 문의드립니다." in text
        assert "감사합니다." in text
        assert "MsoNormal" not in text
        assert "WordSection1" not in text
        assert "xmlns" not in text
        assert "font-family" not in text
