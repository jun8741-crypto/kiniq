# 캐릭터·알 일러스트 디렉토리

이 폴더에 PNG 파일을 두면 EggWidget·CollectionPage·CheckinResultModal에서 자동으로 사용합니다.
파일이 없으면 이모지(🥚🐢🐧🐿️🌟)로 자동 fallback — **0장이어도 정상 동작**.

## 권장 사양

- 포맷: **PNG (투명 배경)**
- 크기: **220 × 220** (Retina 2x, 표시 크기는 110px)
- 배경: 투명 또는 흰색

## 파일명 (정확히 일치해야 함)

### 알 (단계 0 — 부화 전)
```
egg.png
```

### 거북이 🐢 (TURTLE)
```
turtle_stage1.png   ← 부화 직후 (1단계)
turtle_stage2.png   ← 40회 진화
turtle_stage3.png   ← 100회 진화
turtle_stage4.png   ← 200회 완전체
```

### 펭귄 🐧 (PENGUIN)
```
penguin_stage1.png
penguin_stage2.png
penguin_stage3.png
penguin_stage4.png
```

### 다람쥐 🐿️ (SQUIRREL)
```
squirrel_stage1.png
squirrel_stage2.png
squirrel_stage3.png
squirrel_stage4.png
```

## 최소 버전 (4장만 — 시간 부족 시)

알 1장 + 종별 1장만 두면, **단계 구분은 배경 색·테두리·"완전체 ✨" 배지로** 자동 강조됩니다.

```
egg.png
turtle_stage1.png    ← 1·2·3·4단계 모두 이 이미지로 표시
penguin_stage1.png
squirrel_stage1.png
```

코드 변경 불필요 — 일러스트 받으면 그냥 이 폴더에 두기만 하면 됩니다.
