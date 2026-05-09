# ContentFlow 미완성 항목 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ContentFlow Rails 웹 GUI의 미완성 8개 항목을 모두 구현하여 실제 동작 가능한 상태로 만든다.

**Architecture:** Python 백엔드 + Rails 8.1 웹 GUI. Python scripts는 dotenv 기반 config.py로 환경변수 로드. Rails는 Hotwire(Turbo Streams)로 비동기 작업 상태 표시. 번역은 한국어로 통일.

**Tech Stack:** Rails 8.1, Tailwind CSS v4, Hotwire (Turbo + Stimulus), SQLite, Python 3.13, Groq API

---

### Task 1: Python config.py 생성 (dotenv 기반)

**Files:**
- Create: `config.py`

기존 모든 Python 파일이 `from config import Config`를 사용. dotenv로 .env 파일에서 환경변수를 로드하는 Config 클래스 생성.

- [ ] **Step 1: config.py 생성**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
    X_API_KEY = os.environ.get("X_API_KEY")
    X_API_KEY_SECRET = os.environ.get("X_API_KEY_SECRET")
    X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

    INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
```

- [ ] **Step 2: config.py가 동작하는지 확인**

Run: `cd /Users/sekub/socialmedia && source venv/bin/activate && python -c "from config import Config; print('OK')"`
Expected: `OK`

---

### Task 2: 번역 언어 한국어 통일

**Files:**
- Modify: `translator.py` — 페르시아어 프롬프트를 한국어로 변경

- [ ] **Step 1: translator.py의 translate_to_persian 메서드를 translate_to_korean으로 변경**

system prompt를 한국어 번역으로 변경. 메서드명은 기존 호출부와의 호환을 위해 유지하되, 프롬프트만 변경.

- [ ] **Step 2: main.py에서 translate_to_persian 호출 확인 및 유지**

기존 메서드명 `translate_to_persian`은 유지 (호출부가 많으므로). 내부 프롬프트만 한국어로 변경.

---

### Task 3: Geist Mono 폰트 로드

**Files:**
- Modify: `web/app/views/layouts/application.html.erb` — Geist Mono 폰트 CDN 추가

- [ ] **Step 1: layout head에 Geist Mono 폰트 링크 추가**

Google Fonts에서 Geist Mono 로드.

---

### Task 4: Tailwind 테마 보완

**Files:**
- Modify: `web/app/assets/tailwind/application.css` — 폰트 패밀리 추가

- [ ] **Step 1: @theme에 font-family 추가**

Pretendard와 Geist Mono를 Tailwind 테마에 등록.

---

### Task 5: 페이지네이션 구현

**Files:**
- Modify: `web/Gemfile` — pagy gem 추가
- Modify: `web/app/controllers/articles_controller.rb` — pagy 적용
- Modify: `web/app/controllers/dashboard_controller.rb` — pagy 적용
- Modify: `web/app/views/articles/index.html.erb` — 페이지네이션 UI
- Create: `web/config/initializers/pagy.rb` — pagy 설정

- [ ] **Step 1: Gemfile에 pagy 추가하고 bundle install**
- [ ] **Step 2: pagy initializer 생성**
- [ ] **Step 3: ArticlesController에 pagy 적용**
- [ ] **Step 4: articles/index.html.erb에 페이지네이션 UI 추가**

---

### Task 6: Turbo Streams 비동기 진행 상태

**Files:**
- Modify: `web/app/controllers/articles_controller.rb` — scrape/translate/post를 비동기로 변경
- Create: `web/app/views/articles/_scrape_status.html.erb` — 진행 상태 partial
- Modify: `web/app/views/articles/show.html.erb` — turbo frame 추가

스크래핑과 번역 시 Turbo Stream으로 진행 상태를 실시간 표시.

- [ ] **Step 1: scrape 액션을 비동기로 변경 (SolidQueue job)**
- [ ] **Step 2: translate 액션을 Turbo Stream 응답으로 변경**
- [ ] **Step 3: post_to_platform을 Turbo Stream 응답으로 변경**

---

### Task 7: Rails 테스트 추가

**Files:**
- Create: `web/test/test_helper.rb`
- Create: `web/test/models/article_test.rb`
- Create: `web/test/controllers/articles_controller_test.rb`
- Create: `web/test/controllers/dashboard_controller_test.rb`
- Create: `web/test/services/groq_translator_test.rb`

- [ ] **Step 1: test_helper.rb 설정**
- [ ] **Step 2: Article 모델 테스트**
- [ ] **Step 3: DashboardController 테스트**
- [ ] **Step 4: ArticlesController 테스트**

---

### Task 8: Bundle install 확인 및 실행

- [ ] **Step 1: bundle install 실행 확인**

Run: `cd /Users/sekub/socialmedia/web && bundle check`
