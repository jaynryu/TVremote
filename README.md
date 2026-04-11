# Apple TV Remote

macOS에서 Apple TV를 제어하는 리모트 앱입니다.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Swift](https://img.shields.io/badge/Swift-5.9+-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 구성

| 구성 요소 | 경로 | 설명 |
|-----------|------|------|
| **macOS 데스크톱 앱** | `app/` | 서버 없이 단독 실행되는 GUI 앱 (customtkinter + pyatv) |
| **API 서버** | `server/` | FastAPI + pyatv 기반 REST API |
| **웹 리모트** | `server/static/` | 브라우저에서 사용하는 리모트 UI |
| **iOS 앱** | `TVRemote/` | SwiftUI 네이티브 앱 (서버 필요) |

## macOS 데스크톱 앱

서버 없이 Apple TV를 직접 제어하는 단독 실행 앱입니다.

### 기능

- 기기 검색 및 페어링
- D-pad 방향키 / OK 버튼
- 재생 컨트롤 (재생/일시정지, 이전, 다음)
- 볼륨 조절, 메뉴, 홈, 전원
- 키보드 텍스트 입력
- 재생 상태 표시 (5초 자동 갱신)
- 키보드 단축키 (화살표, Enter, Esc, Space)

### 실행 방법

```bash
# 의존성 설치
pip install -r app/requirements.txt

# tkinter가 없는 경우 (macOS)
brew install python-tk@3.12  # Python 버전에 맞게 변경

# 실행
python -m app.main
```

### 초기 설정 (페어링)

앱을 처음 실행하면 Apple TV와 **Companion 프로토콜 페어링**이 필요합니다. 페어링은 전원, 볼륨 등 모든 기능을 사용하기 위해 반드시 필요합니다.

1. 앱 실행 후 자동으로 네트워크의 Apple TV를 검색합니다
2. 기기를 선택하면 페어링 다이얼로그가 표시됩니다
3. Apple TV 화면에 표시된 **4자리 PIN**을 입력합니다
4. 페어링이 완료되면 자동으로 연결됩니다

크레덴셜은 `~/Library/Application Support/TVRemote/credentials.json`에 저장되며, 이후 실행 시 자동으로 연결됩니다.

> 같은 네트워크에 Apple TV와 Mac이 연결되어 있어야 합니다.

### .app 번들 빌드

```bash
cd app
pip install pyinstaller Pillow

# 아이콘 생성
python resources/make_icon.py

# 빌드
pyinstaller build.spec --noconfirm

# 데스크탑에 복사
cp -R dist/"TV Remote.app" ~/Desktop/
```

> 처음 실행 시 **우클릭 → 열기**로 macOS 보안 경고를 우회할 수 있습니다.

## API 서버 + 웹 리모트

iOS 앱이나 브라우저에서 사용할 때 필요합니다.

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

브라우저에서 `http://localhost:8000` 접속하면 웹 리모트를 사용할 수 있습니다.

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/devices` | 기기 검색 |
| POST | `/devices/{id}/pair` | 페어링 시작 |
| POST | `/devices/{id}/pair/pin` | PIN 입력 |
| POST | `/devices/{id}/connect` | 연결 |
| POST | `/devices/{id}/disconnect` | 연결 해제 |
| POST | `/remote/{command}` | 리모트 명령 전송 |
| POST | `/remote/power/toggle` | 전원 토글 |
| POST | `/keyboard` | 텍스트 전송 |
| GET | `/status` | 재생 상태 조회 |

## iOS 앱

Xcode에서 `TVRemote/TVRemote.xcodeproj`를 열고 빌드합니다. API 서버가 실행 중이어야 합니다.

## 키보드 단축키 (데스크톱 앱 / 웹)

| 키 | 동작 |
|----|------|
| ↑ ↓ ← → | 방향 이동 |
| Enter | 선택 |
| Esc | 메뉴 (뒤로) |
| Space | 재생/일시정지 |
