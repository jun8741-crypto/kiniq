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
