# 캐릭터·알 일러스트 디렉토리

이 폴더에 PNG 또는 SVG 파일을 두면 EggWidget·CollectionPage·CheckinResultModal에서 자동 사용.
파일이 없으면 이모지(🥚🐢🐧🐿️🌟) fallback — **0장이어도 정상 동작**.

기본 SVG 10장이 동봉되어 있으므로 PNG 교체 안 해도 시연 가능합니다.

## 권장 사양

- 포맷: **PNG (투명 배경)** 또는 SVG
- 크기: **220 × 220** (Retina 2x, 표시 크기는 110px)
- 배경: 투명 또는 흰색

## 파일명 (정확히 일치해야 함)

### 알 (단계 0 — 부화 전)
```
egg.svg  (또는 egg.png)
```

### 거북이 🐢 (TURTLE)
```
turtle_stage1.svg   ← 부화 직후 (1단계)
turtle_stage2.svg   ← 40회 진화
turtle_stage3.svg   ← 100회 최종 진화 (완전체, 왕관·후광)
```

### 펭귄 🐧 (PENGUIN)
```
penguin_stage1.svg
penguin_stage2.svg
penguin_stage3.svg
```

### 다람쥐 🐿️ (SQUIRREL)
```
squirrel_stage1.svg
squirrel_stage2.svg
squirrel_stage3.svg
```

## PNG로 교체하려면

`src/api/gamification.ts`의 `characterImagePath` 함수에서 `.svg` → `.png`로 한 줄만 변경.
일부만 교체하려면 fallback 체인(.png 시도 → 실패 시 .svg → 실패 시 이모지) 구현 가능 — Claude에게 요청.

## 최소 버전 (4장만 — 시간 부족 시)

알 1장 + 종별 1장(stage1)만 두면, **단계 구분은 배경 색·테두리·"완전체 ✨" 배지로** 자동 강조됩니다.

```
egg.svg
turtle_stage1.svg    ← 1·2·3단계 모두 이 이미지로 표시
penguin_stage1.svg
squirrel_stage1.svg
```
