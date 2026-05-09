# Design System — ContentFlow

## Product Context
- **What this is:** TechCrunch 기사를 스크래핑해 한국어로 번역하고, 인스타그램 카드뉴스/텔레그램/X에 자동 포스팅하는 콘텐츠 자동화 도구
- **Who it's for:** 개인 운영자 (1인 콘텐츠 자동화 대시보드)
- **Space/industry:** 소셜미디어 마케팅 자동화
- **Project type:** Web app (대시보드 + 카드뉴스 에디터)
- **Memorable thing:** "진짜 프로가 쓰는 도구"

## Aesthetic Direction
- **Direction:** Industrial Minimal — Claude + Linear 느낌
- **Decoration level:** Minimal — 타이포그래피와 여백이 디자인을 이끈다
- **Mood:** 절제되고 어두운, 데이터 중심의 전문 도구. 화려한 장식 없이 콘텐츠에 집중.

## Typography
- **Display/Hero:** Pretendard 800 — 한국어+영문 혼용 최적화, 깔끔한 산세리프
- **Body:** Pretendard 400 — 높은 가독성, 다양한 웨이트 지원
- **UI/Labels:** Pretendard 550 — 버튼, 네비게이션, 배지 등 UI 요소
- **Data/Tables:** Geist Mono — tabular-nums 지원, 숫자/날짜/코드 표시용
- **Code:** Geist Mono
- **Loading:** Pretendard via jsDelivr CDN, Geist Mono via Google Fonts
- **Scale:**
  - xs: 11px — 보조 텍스트, 타임스탬프
  - sm: 13px — UI 라벨, 배지, 캡션
  - base: 15px — 본문
  - lg: 18px — 섹션 제목
  - xl: 20px — 서브 헤딩
  - 2xl: 24px — 페이지 타이틀
  - 3xl: 36px — 히어로/디스플레이

## Color
- **Approach:** Restrained — 1 accent + neutrals, 색상은 의미 있는 곳에만
- **Background:** #0A0A0A — near-black
- **Surface/Card:** #171717
- **Surface Hover:** #1E1E1E
- **Border:** #262626
- **Border Subtle:** #1F1F1F
- **Text:** #FAFAFA
- **Text Muted:** #A1A1AA
- **Text Dim:** #71717A
- **Accent:** #D4A574 — warm sand, Claude의 따뜻한 톤에서 영감
- **Accent Hover:** #E0B88A
- **Accent Muted:** rgba(212,165,116,0.15)
- **Semantic:**
  - Success: #4ADE80 / muted: rgba(74,222,128,0.15)
  - Warning: #FBBF24 / muted: rgba(251,191,36,0.15)
  - Error: #F87171 / muted: rgba(248,113,113,0.15)
  - Info: #60A5FA / muted: rgba(96,165,250,0.15)

## Spacing
- **Base unit:** 4px
- **Density:** Comfortable
- **Scale:**
  - 2xs: 2px
  - xs: 4px
  - sm: 8px
  - md: 16px
  - lg: 24px
  - xl: 32px
  - 2xl: 48px
  - 3xl: 64px

## Layout
- **Approach:** Grid-disciplined — 사이드바(240px) + 메인 영역
- **Grid:** 사이드바 고정, 메인 영역 fluid
- **Max content width:** 1200px
- **Border radius:**
  - sm: 6px — 버튼, 입력, 배지
  - md: 8px — 카드, 테이블 래퍼
  - lg: 12px — 모달, 큰 패널
  - full: 9999px — 배지 pill, 아바타

## Motion
- **Approach:** Minimal-functional — 상태 전환만, 화려한 애니메이션 없음
- **Easing:** enter(ease-out) exit(ease-in) move(ease-in-out)
- **Duration:**
  - micro: 50-100ms — 호버, 포커스
  - short: 150ms — 버튼 상태, 토글
  - medium: 250ms — 패널 열기/닫기
  - long: 400ms — 페이지 전환

## Component Patterns (shadcn)
- **Buttons:** Primary(accent bg, dark text), Secondary(surface bg, border), Ghost(transparent)
- **Badges:** Pill 형태, dot indicator + muted background
- **Tables:** surface bg, subtle border, hover row highlight
- **Cards:** surface bg, border, no shadow
- **Inputs:** bg background, border, accent focus ring
- **Alerts:** semantic muted background + semantic text color

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | 디자인 시스템 생성 | /design-consultation — Claude dark + shadcn 기반, "진짜 프로가 쓰는 도구" 컨셉 |
| 2026-05-09 | Pretendard 폰트 선택 | 한국어+영문 혼용에 최적화된 산세리프, 다양한 웨이트 지원 |
| 2026-05-09 | Warm sand accent (#D4A574) | 블루/퍼플 대신 따뜻한 톤으로 차별화, Claude의 인간적 느낌 반영 |
| 2026-05-09 | 다크 모드 only | 프로 도구 특성상 다크 기본, 라이트 모드 미지원 |
