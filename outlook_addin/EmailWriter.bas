Attribute VB_Name = "EmailWriter"
Option Explicit

' === 설정 ===
Const SERVER_URL As String = "http://localhost:8599"
Const API_ENDPOINT As String = "/api/generate-email"
Const REQUEST_TIMEOUT As Long = 30000  ' 30초

' ============================================================
' 메인 진입점: 이메일 생성
' ============================================================
Sub GenerateEmail()
    Dim inspector As Outlook.inspector
    Set inspector = Application.ActiveInspector

    If inspector Is Nothing Then
        MsgBox "열려있는 메일 편집기가 없습니다.", vbExclamation
        Exit Sub
    End If

    Dim mailItem As Outlook.mailItem
    Set mailItem = inspector.CurrentItem

    ' 1. 메일 전체 본문 (HTML)
    Dim fullBody As String
    fullBody = mailItem.HTMLBody

    ' 2. 선택된 텍스트 (Word Editor 사용)
    Dim wordEditor As Object
    Set wordEditor = inspector.WordEditor
    Dim selectedText As String
    selectedText = wordEditor.Application.Selection.Text

    If Len(Trim(selectedText)) = 0 Then
        MsgBox "이메일 본문에서 텍스트를 블록 선택한 후 실행하세요.", vbExclamation
        Exit Sub
    End If

    ' 3. 메타데이터
    Dim toRecipients As String
    toRecipients = mailItem.To
    Dim subject As String
    subject = mailItem.subject
    Dim isReply As Boolean
    isReply = IsReplyMail(subject)

    ' 4. 추가 프롬프트
    Dim additionalPrompt As String
    additionalPrompt = ShowPromptDialog()

    ' 5. JSON 구성 및 전송
    Dim json As String
    json = BuildJson(fullBody, selectedText, toRecipients, subject, isReply, additionalPrompt)

    Dim response As String
    response = SendRequest(json)

    ' 6. 응답 파싱 후 선택 영역 대체
    Dim generatedText As String
    generatedText = ParseResponse(response)

    If Len(generatedText) > 0 Then
        wordEditor.Application.Selection.Text = generatedText
    End If
End Sub

' ============================================================
' JSON 빌드
' ============================================================
Function BuildJson(fullBody As String, selectedText As String, _
                   toRecipients As String, subject As String, _
                   isReply As Boolean, additionalPrompt As String) As String
    BuildJson = "{" & _
        """full_body"": """ & EscapeJson(fullBody) & """," & _
        """selected_text"": """ & EscapeJson(selectedText) & """," & _
        """to_recipients"": """ & EscapeJson(toRecipients) & """," & _
        """subject"": """ & EscapeJson(subject) & """," & _
        """is_reply"": " & IIf(isReply, "true", "false") & "," & _
        """additional_prompt"": """ & EscapeJson(additionalPrompt) & """" & _
    "}"
End Function

Function EscapeJson(text As String) As String
    Dim result As String
    result = Replace(text, "\", "\\")
    result = Replace(result, """", "\""")
    result = Replace(result, vbCr, "\r")
    result = Replace(result, vbLf, "\n")
    result = Replace(result, vbTab, "\t")
    EscapeJson = result
End Function

' ============================================================
' HTTP 전송
' ============================================================
Function SendRequest(jsonPayload As String) As String
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")

    http.Open "POST", SERVER_URL & API_ENDPOINT, False
    http.setRequestHeader "Content-Type", "application/json; charset=utf-8"
    http.Send jsonPayload

    SendRequest = http.responseText
End Function

' ============================================================
' JSON 응답 파싱
' ============================================================
Function ParseResponse(jsonText As String) As String
    ' JSON 응답에서 "generated_text" 값을 추출
    ' 서버 응답 구조: {"success":true,"generated_text":"...","error_message":null}

    Dim key As String
    key = """generated_text"": """

    Dim startPos As Long
    startPos = InStr(1, jsonText, key)

    If startPos = 0 Then
        ' generated_text 키를 찾지 못함 - 에러 메시지 확인
        Dim errKey As String
        errKey = """error_message"": """
        Dim errPos As Long
        errPos = InStr(1, jsonText, errKey)
        If errPos > 0 Then
            Dim errStart As Long
            errStart = errPos + Len(errKey)
            Dim errEnd As Long
            errEnd = InStr(errStart, jsonText, """")
            MsgBox "서버 에러: " & Mid(jsonText, errStart, errEnd - errStart), vbCritical
        Else
            MsgBox "서버 응답을 파싱할 수 없습니다.", vbCritical
        End If
        ParseResponse = ""
        Exit Function
    End If

    ' 값 시작 위치 (키 + 따옴표 이후)
    Dim valueStart As Long
    valueStart = startPos + Len(key)

    ' 값 끝 위치 찾기 (이스케이프되지 않은 따옴표)
    Dim valueEnd As Long
    Dim i As Long
    i = valueStart
    Do While i <= Len(jsonText)
        If Mid(jsonText, i, 1) = """" Then
            If i > 1 And Mid(jsonText, i - 1, 1) <> "\" Then
                valueEnd = i
                Exit Do
            ElseIf i = 1 Then
                valueEnd = i
                Exit Do
            End If
        End If
        i = i + 1
    Loop

    Dim rawValue As String
    rawValue = Mid(jsonText, valueStart, valueEnd - valueStart)

    ' JSON 이스케이프 시퀀스 복원
    rawValue = Replace(rawValue, "\n", vbLf)
    rawValue = Replace(rawValue, "\r", vbCr)
    rawValue = Replace(rawValue, "\t", vbTab)
    rawValue = Replace(rawValue, "\""", """")
    rawValue = Replace(rawValue, "\\", "\")

    ParseResponse = rawValue
End Function

' ============================================================
' 추가 프롬프트 입력
' ============================================================
Function ShowPromptDialog() As String
    ShowPromptDialog = InputBox( _
        "추가 지시사항을 입력하세요 (선택사항):", _
        "이메일 작성 도우미", _
        "")
End Function

' ============================================================
' 회신 메일 판별 (다국어 지원)
' ============================================================
Function IsReplyMail(subject As String) As Boolean
    ' 영문: "RE:", "Re:", "re:"
    ' 한국어: "답장:", "회신:"

    Dim upperSubject As String
    upperSubject = UCase(Trim(subject))

    If Left(upperSubject, 3) = "RE:" Then
        IsReplyMail = True
        Exit Function
    End If

    Dim trimSubject As String
    trimSubject = Trim(subject)

    If Left(trimSubject, 3) = "답장:" Then
        IsReplyMail = True
        Exit Function
    End If

    If Left(trimSubject, 3) = "회신:" Then
        IsReplyMail = True
        Exit Function
    End If

    IsReplyMail = False
End Function
