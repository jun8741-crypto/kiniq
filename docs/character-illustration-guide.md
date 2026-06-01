# 캐릭터 일러스트 — AI 생성 가이드

현재 13장의 **SVG 임시 일러스트**가 `frontend/ckd-care-app/public/characters/`에 포함되어 있어 발표 시연이 가능한 상태입니다. 더 고품질 일러스트로 교체하고 싶다면 아래 AI 프롬프트를 사용하세요.

## 🎨 톤 가이드 (모든 캐릭터 공통)

- **스타일**: 카와이(kawaii) / 카카오 캐릭터 / 산리오 톤 — 둥글둥글 귀여움
- **컬러**: 파스텔·생동감 있는 채도
- **표정**: 큰 눈·환한 미소 (CKD 환자 격려용)
- **포즈**: 정면, 손 보임, 안정감 있는 자세
- **배경**: 투명 또는 흰색 (alpha PNG)
- **사이즈**: 정사각, 1024×1024 권장 (220×220로 다운스케일)

## 📋 컬러 팔레트

| 종 | 메인 | 서브 | 강조 |
|---|---|---|---|
| 거북이 🐢 | #16A34A (초록) | #86EFAC (연두) | #065F46 (진초록) |
| 펭귄 🐧 | #1F2937 (검정) | #F9FAFB (흰색) | #F59E0B (노랑부리) |
| 다람쥐 🐿️ | #92400E (갈색) | #FDE68A (베이지) | #D97706 (주황꼬리) |

## 📝 프롬프트 13개 (영어 — DALL-E·Midjourney·Stable Diffusion 호환)

### 알 (egg.png)
```
A cute cartoon egg mascot for a health app, smooth oval shape, soft cream
color #FEF3C7 with golden #FBBF24 spots, gentle highlights, subtle smile,
kawaii style, sanrio-inspired, simple flat illustration, transparent
background, centered, 1:1 ratio
```

### 거북이 1단계 (turtle_stage1.png)
```
Cute baby turtle character for kidney health app, small round body, dark
green #16A34A shell with hexagon pattern, light green #86EFAC head and
limbs, big sparkly eyes, gentle smile, sitting pose, kawaii sanrio style,
transparent background, flat clean illustration
```

### 거북이 2단계 (turtle_stage2.png)
```
Slightly bigger cute turtle, dark green shell with detailed hexagon
pattern, glossy highlight on shell, red bow tie on head with golden
center, light green limbs, big shiny eyes, friendly smile, kawaii style,
transparent background
```

### 거북이 3단계 (turtle_stage3.png)
```
Confident young turtle character, larger size, vivid green shell with
multiple hexagon patterns, blue scarf around neck, brave expression, big
expressive eyes, two stars in background (yellow #FBBF24), kawaii heroic
pose, transparent background
```

### 거북이 4단계 (turtle_stage4.png)
```
Majestic adult turtle hero with golden crown, deep emerald shell with
intricate hexagon patterns, magical yellow aura glow #FBBF24, sparkles
around, jeweled crown with red and blue gems, regal stance, kawaii
ultimate evolution form, transparent background
```

### 펭귄 1단계 (penguin_stage1.png)
```
Cute baby penguin chick, round black #1F2937 body, white #F9FAFB belly,
orange #F59E0B feet and beak, large sparkling eyes, small flipper-arms,
shy gentle smile, pink cheek blush, kawaii sanrio style, transparent
background
```

### 펭귄 2단계 (penguin_stage2.png)
```
Cute young penguin with checkered red and yellow scarf around neck,
slightly taller body, bright eyes, confident friendly smile, orange beak
and feet, kawaii illustration, soft pastel shading, transparent
background
```

### 펭귄 3단계 (penguin_stage3.png)
```
Brave penguin explorer with blue triangular hat with yellow pompom, gold
star medal on chest with red ribbon, bigger body, determined expression,
shiny eyes, kawaii heroic pose, sparkles around, transparent background
```

### 펭귄 4단계 (penguin_stage4.png)
```
Royal majestic penguin with golden jeweled crown with red and blue gems,
glowing golden aura, red diamond brooch on chest, ultimate evolved form,
serene confident expression, sparkles and stars around, kawaii style,
transparent background
```

### 다람쥐 1단계 (squirrel_stage1.png)
```
Cute baby squirrel with big fluffy brown #92400E tail (curled up), light
beige #FDE68A belly, large ears with cream inner, big bright eyes, tiny
front teeth showing, holding hands close to chest, kawaii sanrio style,
transparent background
```

### 다람쥐 2단계 (squirrel_stage2.png)
```
Young squirrel with even bigger fluffy tail (more volume, soft gradient),
holding a brown acorn with dark cap, light belly, ear tufts, cheerful
expression, kawaii style, transparent background, soft pastel lighting
```

### 다람쥐 3단계 (squirrel_stage3.png)
```
Adventurer squirrel with large fluffy gradient tail, blue scarf, holding
a shiny golden acorn, confident expression, sparkly eyes, two stars in
background, kawaii heroic pose, transparent background
```

### 다람쥐 4단계 (squirrel_stage4.png)
```
Legendary squirrel king with golden crown with jewels, massive sparkling
fluffy tail with golden streaks, glowing yellow aura, holding a diamond-
shaped acorn gem, star medal on chest, ultimate evolution, kawaii regal
pose, magical sparkles, transparent background
```

## 🛠️ 사용 방법

### 방법 0. Google Gemini (제미나이) — 무료 최우선 추천 ⭐️

**왜 추천**:
- 무료 (Google 계정만 있으면 됨)
- 한국어 프롬프트 잘 이해
- Imagen 3 모델 기반, 캐릭터·일러스트 강함
- 한 번에 여러 변형 제공

**접속**:
1. https://gemini.google.com 접속 (구글 계정 로그인)
2. 입력창 옆 "이미지 생성" 또는 그냥 프롬프트만 입력해도 자동 인식

**Gemini 프롬프트 팁**:
- 첫 줄에 한국어로 무엇을 그릴지 명시
- "투명 배경", "정사각형 1024×1024", "PNG 형식" 명시
- "마스코트", "카와이", "카카오 캐릭터 스타일" 등 키워드
- 결과가 마음에 안 들면 "더 귀엽게", "눈을 더 크게", "왕관을 황금색으로" 등 추가 지시

**한국어 프롬프트 13개 (Gemini 최적화)**:

#### 알
```
신장 건강 앱 마스코트용 귀여운 알 캐릭터를 그려줘.
- 부드러운 크림색(#FEF3C7) 본체에 황금색(#FBBF24) 점박이
- 살짝 웃는 표정과 부드러운 하이라이트
- 카카오 캐릭터 같은 카와이 스타일, 둥글둥글
- 투명 배경, 정사각형 1024x1024, PNG
```

#### 거북이 1단계
```
신장 건강 앱 마스코트용 아기 거북이를 그려줘.
- 짙은 초록색(#16A34A) 등껍질에 육각형 패턴
- 연두색(#86EFAC) 머리와 손발
- 큰 반짝이는 눈, 살짝 웃는 표정, 분홍색 볼터치
- 4개의 작은 다리로 앉아 있는 포즈
- 카와이 산리오 스타일, 투명 배경, 1024x1024 PNG
```

#### 거북이 2단계
```
거북이 1단계보다 살짝 큰 청소년 거북이를 그려줘.
- 짙은 초록색 등껍질 + 육각형 패턴 + 윤기 하이라이트
- 머리 위에 빨간 리본 (가운데 황금색 단추)
- 더 환한 미소, 큰 눈, 분홍 볼터치
- 카와이 스타일, 투명 배경, 1024x1024 PNG
```

#### 거북이 3단계
```
자신감 넘치는 청년 거북이를 그려줘.
- 더 크고 선명한 초록 등껍질 + 다채로운 육각형 패턴
- 목에 파란색 스카프
- 양옆에 노란 별 2개
- 용감한 표정, 반짝이는 눈
- 카와이 영웅 포즈, 투명 배경, 1024x1024 PNG
```

#### 거북이 4단계 (완전체)
```
신장 건강 앱의 최종 진화 거북이 마스코트, 왕의 풍모.
- 깊은 에메랄드 등껍질, 정교한 육각형 패턴
- 머리에 황금 왕관 (빨강·파랑 보석 박힘)
- 황금색 후광(#FBBF24)이 캐릭터를 감싼 모양
- 주변에 작은 별과 반짝이
- 위엄 있지만 귀여운 표정
- 카와이 궁극 형태, 투명 배경, 1024x1024 PNG
```

#### 펭귄 1단계
```
신장 건강 앱 마스코트용 아기 펭귄을 그려줘.
- 동그란 검정(#1F2937) 본체 + 흰색(#F9FAFB) 배
- 주황색(#F59E0B) 부리와 발
- 크고 반짝이는 눈, 수줍은 미소, 분홍 볼터치
- 양쪽 작은 날개(손)
- 카와이 산리오 스타일, 투명 배경, 1024x1024 PNG
```

#### 펭귄 2단계
```
청소년 펭귄, 1단계보다 살짝 큼.
- 빨간색·노란색 체크무늬 스카프
- 환한 미소, 큰 눈, 분홍 볼터치
- 주황 부리와 발
- 카와이 일러스트, 투명 배경, 1024x1024 PNG
```

#### 펭귄 3단계
```
탐험가 펭귄 캐릭터를 그려줘.
- 파란색 삼각 모자(끝에 황금 폼폼)
- 가슴에 황금 별 메달 (빨간 리본)
- 더 큰 몸, 자신감 있는 표정, 반짝이는 눈
- 주변에 작은 별 2개
- 카와이 영웅 포즈, 투명 배경, 1024x1024 PNG
```

#### 펭귄 4단계 (완전체)
```
펭귄 황제, 최종 진화 형태.
- 머리에 황금 보석 왕관 (빨강·파랑 보석)
- 가슴에 빨간 다이아몬드 브로치
- 황금색 후광이 캐릭터를 감쌈
- 주변에 별과 반짝이 다수
- 차분하고 위엄있지만 귀여운 표정
- 카와이 궁극 형태, 투명 배경, 1024x1024 PNG
```

#### 다람쥐 1단계
```
신장 건강 앱 마스코트용 아기 다람쥐를 그려줘.
- 갈색(#92400E) 몸 + 베이지(#FDE68A) 배
- 크고 폭신한 갈색 꼬리 (살짝 말려 있음)
- 큰 귀(안쪽 베이지), 큰 반짝이는 눈
- 작은 앞니 2개 살짝 보임, 분홍 볼터치
- 양손을 가슴 가까이 모은 귀여운 포즈
- 카와이 산리오 스타일, 투명 배경, 1024x1024 PNG
```

#### 다람쥐 2단계
```
청소년 다람쥐, 더 풍성한 꼬리.
- 더 크고 풍성한 황금빛 그라데이션 꼬리
- 한 손에 갈색 도토리 들고 있음
- 베이지 배, 귀 안쪽 베이지
- 큰 눈, 활기찬 표정
- 카와이 스타일, 투명 배경, 1024x1024 PNG
```

#### 다람쥐 3단계
```
모험가 다람쥐를 그려줘.
- 크고 풍성한 그라데이션 꼬리
- 목에 파란색 스카프
- 한 손에 황금 도토리
- 양옆에 노란 별 2개
- 자신감 있는 표정, 반짝이는 눈
- 카와이 영웅 포즈, 투명 배경, 1024x1024 PNG
```

#### 다람쥐 4단계 (완전체)
```
전설의 다람쥐 왕, 최종 진화.
- 머리에 황금 왕관 (보석 박힘)
- 거대하고 화려한 꼬리 (황금빛 광채)
- 한 손에 다이아몬드 도토리
- 가슴에 별 메달
- 황금 후광이 감쌈, 주변에 마법 반짝이
- 위엄 있지만 귀여운 카와이 표정
- 카와이 궁극 형태, 투명 배경, 1024x1024 PNG
```

**Gemini 사용 흐름**:
1. 위 프롬프트 중 하나를 복사해서 Gemini에 붙여넣기
2. 결과 1~4장 제공 → 마음에 드는 것 우클릭 → "이미지 저장"
3. 파일명을 정확히 맞춰서 저장: 예) `turtle_stage1.png`
4. `frontend/ckd-care-app/public/characters/` 폴더에 저장
5. 13장 다 완료 후 **코드 한 줄 변경** (아래 "PNG 적용 방법" 참조)

### 방법 1. Microsoft Designer / Bing Image Creator (무료 추천)
1. https://designer.microsoft.com 또는 https://www.bing.com/images/create 접속
2. Microsoft 계정 로그인 (무료)
3. 위 프롬프트 복붙 → 생성 (1회 4장 변형 제공)
4. 마음에 드는 것 다운로드
5. **파일명을 정확히 맞춰서** `frontend/ckd-care-app/public/characters/` 에 저장
   - 예: `turtle_stage1.png` (소문자, 언더스코어)
6. 코드는 `.svg` 우선이므로, PNG로 교체하려면:
   - 기존 SVG 삭제 또는 그대로 두기 (브라우저는 정확한 확장자 매칭)
   - `gamification.ts` 의 `characterImagePath`에서 `.svg`를 `.png`로 변경

### 방법 2. ChatGPT Plus (DALL-E 3)
1. ChatGPT Plus 구독 중이면 영문 프롬프트 그대로 입력
2. "Make this transparent background PNG" 추가

### 방법 3. Leonardo.AI (무료 150토큰/일)
1. https://leonardo.ai 가입
2. "Anime" 또는 "Cute Cartoon" 모델 선택
3. 프롬프트 입력 → Style: Kawaii / Chibi

## 🔄 PNG 적용 방법 (Gemini 결과물 받은 후)

13장 다 받으면, 폴더에 두고 코드 한 줄만 바꾸면 됩니다.

**1. 파일을 정확한 이름으로 저장**:
```
frontend/ckd-care-app/public/characters/
├── egg.png
├── turtle_stage1.png ~ turtle_stage4.png
├── penguin_stage1.png ~ penguin_stage4.png
└── squirrel_stage1.png ~ squirrel_stage4.png
```

**2. `src/api/gamification.ts`에서 확장자 한 줄 변경**:
```ts
// 변경 전 (현재 SVG)
return `/characters/${slug}_stage${safeStage}.svg`;

// 변경 후 (PNG 적용)
return `/characters/${slug}_stage${safeStage}.png`;
```
egg도 같은 함수 안의 `egg.svg`를 `egg.png`로 변경.

**3. 기존 SVG는 그대로 둬도 됩니다** (PNG 우선 사용, 파일은 보존).

**4. 일부만 PNG로 교체하고 싶으면**:
- 받은 것만 PNG로 저장, 나머지는 SVG 유지
- 확장자 fallback 체인 구현 가능 (.png → .svg → 이모지)

**부분 교체 fallback 원하시면 말씀해주세요 — 5분 안에 구현해드림.**

## 🎯 시간 절약 팁

- **모두 다 만들 시간 없으면**: stage1만 4장 생성하고, stage2~4는 동일 이미지로 복사 (단계 강조는 EggWidget 코드의 색·배지가 처리)
  ```bash
  cp turtle_stage1.png turtle_stage2.png
  cp turtle_stage1.png turtle_stage3.png
  cp turtle_stage1.png turtle_stage4.png
  ```
- **알 1장 + 종별 1장 = 최소 4장만 있어도 발표 가능**.

## 🔄 SVG → PNG 변환 (선택)

기본 SVG를 PNG로 변환하려면:
- 온라인: https://svgtopng.com 또는 https://cloudconvert.com
- Inkscape (무료 데스크탑): File → Export PNG (1024×1024)
- Figma (무료): SVG 임포트 → Export PNG 2x
