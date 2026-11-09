# WeasyPrint Windows 설치 가이드

## 1. MSYS2 설치
- https://www.msys2.org/
- 기본 경로 `C:\msys64`로 설치
- 시작 메뉴에서 **MSYS2 UCRT64** 실행

## 2. Pango 설치

MSYS2 UCRT64 터미널에서 실행합니다.

```bash
pacman -S mingw-w64-ucrt-x86_64-pango
```

설치 확인 메시지에 `Y` 입력 후 Enter.

## 3. Windows DLL 경로 설정

CMD를 새로 실행하고 입력합니다.

```cmd
set "WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin"
```

## 4. WeasyPrint 실행 확인

```cmd
python -m weasyprint --info
```

정상적으로 정보가 출력되면 설치 완료입니다.

## 5. PDF 빌드

```cmd
cd /d C:\Users\kbhj0\resume
python build_pdf.py
```

특정 문서만 빌드하려면:

```cmd
python build_pdf.py --only resume
```

사용 가능한 옵션:
- resume
- portfolio
- cover
- application

## 6. 오류 발생 시

DLL 존재 여부 확인:

```cmd
dir C:\msys64\ucrt64\bin\libgobject-2.0-0.dll
```

파일이 없으면 MSYS2 UCRT64에서 Pango 설치 명령을 다시 실행합니다.

## 참고
- https://doc.courtbouillon.org/weasyprint/stable/first_steps.html
- https://www.msys2.org/