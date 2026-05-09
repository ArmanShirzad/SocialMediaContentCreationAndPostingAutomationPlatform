# ContentFlow Web GUI — Design Spec

## Overview
TechCrunch 기사를 한국어로 번역하고 소셜미디어에 자동 포스팅하는 도구의 웹 GUI.
Python CLI 백엔드 위에 Rails 웹 인터페이스를 구축한다.

## Architecture

```
[Browser] <--Hotwire--> [Rails 8 App] --system call--> [Python Scripts]
                              |
                         [SQLite DB]
                         (articles.db)
```

- **Rails 8.1** + Hotwire (Turbo + Stimulus)
- **SQLite** — 기존 Python의 articles.db 스키마를 Rails migration으로 재현
- **Python 연동** — `Open3.capture3`로 Python 스크립트 호출 (venv 경로 포함)
- **디자인** — DESIGN.md 기반. Tailwind CSS로 구현. shadcn 패턴.

## Data Model

### Article
기존 Python DB의 articles 테이블과 동일한 스키마:

| Column | Type | Description |
|--------|------|-------------|
| id | integer | PK |
| title | string | 원문 제목 |
| url | string | 원문 URL (unique) |
| content | text | 원문 내용 |
| translated_title | string | 한국어 제목 |
| translated_content | text | 한국어 내용 |
| summary | text | 인스타그램용 요약 |
| post_datetime | datetime | 원문 게시일 |
| image_url | string | 원문 이미지 URL |
| crawl_datetime | datetime | 스크래핑 시각 |
| posted_to_telegram | boolean | 텔레그램 포스팅 여부 |
| posted_to_instagram | boolean | 인스타그램 포스팅 여부 |
| posted_to_x | boolean | X 포스팅 여부 |
| created_at | datetime | 생성 시각 |
| updated_at | datetime | 수정 시각 |

## Pages & Routes

### 1. Dashboard (`GET /`)
- 통계 카드: 전체 기사 수, 포스팅 완료, 대기중, 실패
- 최근 기사 테이블: 제목, 상태 배지, 플랫폼별 아이콘, 날짜
- 검색 + 새 기사 스크래핑 버튼

### 2. Articles (`GET /articles`, `GET /articles/:id`)
- 기사 목록 (페이지네이션)
- 기사 상세: 원문 + 번역문 보기, 포스팅 상태, 수동 포스팅 버튼

### 3. Card News (`GET /card_news/new`, `POST /card_news`)
- 기사 선택 드롭다운
- 번역된 제목/내용 편집
- 인스타그램 카드뉴스 미리보기 (폰 프레임)
- 생성 + 포스팅 버튼

### 4. Settings (`GET /settings`)
- API 키 관리 (Groq, Pexels, Telegram, X, Instagram)
- 자동화 설정 (스케줄 간격, 기사 수 제한)

## Key Interactions

### 기사 스크래핑
1. 사용자가 "새 기사 스크래핑" 클릭
2. Rails → `python scraper.py` 호출 (Turbo Stream으로 진행 상태 표시)
3. 스크래핑 결과를 DB에 저장
4. 대시보드 자동 업데이트

### 번역
1. 기사 상세에서 "번역" 클릭
2. Rails → Groq API 직접 호출 (Python 없이 Rails에서 HTTP 요청)
3. 번역 결과 DB 저장, 화면 업데이트

### 카드뉴스 생성 & 포스팅
1. 기사 선택 → 번역 내용 자동 로드
2. 편집 후 미리보기 확인
3. "Instagram 포스팅" → Rails에서 Python instagram_poster.py 호출

## Frontend Stack
- **Tailwind CSS** — DESIGN.md의 색상/스페이싱을 CSS custom properties로 정의
- **Turbo Frames** — 부분 페이지 업데이트 (기사 목록, 상태 변경)
- **Turbo Streams** — 실시간 상태 업데이트 (스크래핑/포스팅 진행)
- **Stimulus** — 카드뉴스 미리보기 실시간 반영, 폼 인터랙션

## Directory Structure

```
web/                          # Rails 앱 루트
├── app/
│   ├── controllers/
│   │   ├── dashboard_controller.rb
│   │   ├── articles_controller.rb
│   │   ├── card_news_controller.rb
│   │   └── settings_controller.rb
│   ├── models/
│   │   └── article.rb
│   ├── views/
│   │   ├── layouts/application.html.erb
│   │   ├── shared/_sidebar.html.erb
│   │   ├── dashboard/index.html.erb
│   │   ├── articles/index.html.erb
│   │   ├── articles/show.html.erb
│   │   ├── card_news/new.html.erb
│   │   └── settings/index.html.erb
│   ├── javascript/
│   │   └── controllers/        # Stimulus controllers
│   │       ├── card_preview_controller.js
│   │       └── scrape_controller.js
│   └── services/
│       ├── python_runner.rb     # Python 스크립트 실행 래퍼
│       ├── groq_translator.rb   # Groq API 번역 서비스
│       └── scraper_service.rb   # 스크래핑 서비스
├── config/
│   └── routes.rb
├── db/
│   └── migrate/
└── Gemfile
```

## Non-Goals (v1)
- 사용자 인증 (개인용이므로 불필요)
- YouTube 업로드 GUI
- 비디오 생성 GUI
- 라이트 모드
- 모바일 최적화 (데스크탑 우선)
