"""부화 시 캐릭터 이름 자동 생성 — 형용사 + 종별 한국어 별칭."""

import secrets

from app.models.gamification import CharacterSpecies

ADJECTIVES = [
    "고결한",
    "호기심 많은",
    "용맹한",
    "재빠른",
    "온화한",
    "장난스러운",
    "당당한",
    "총명한",
    "포근한",
    "씩씩한",
    "느긋한",
    "꾸준한",
]

SPECIES_NICKNAMES: dict[CharacterSpecies, list[str]] = {
    CharacterSpecies.TURTLE: ["파랑", "또롱", "거북이", "퍼북", "구이"],
    CharacterSpecies.PENGUIN: ["차마", "포포", "펭귄", "쮸쮸", "콩이"],
    CharacterSpecies.SQUIRREL: ["찌이", "쪼롱", "다람", "도토리", "꼬리"],
    CharacterSpecies.RABBIT: ["토토", "깡총", "복실", "당근", "푸딩"],
    CharacterSpecies.PANDA: ["봉봉", "댓잎", "둥글", "판판", "뽀뽀"],
}

SPECIES_EMOJI: dict[CharacterSpecies, str] = {
    CharacterSpecies.TURTLE: "🐢",
    CharacterSpecies.PENGUIN: "🐧",
    CharacterSpecies.SQUIRREL: "🐿️",
    CharacterSpecies.RABBIT: "🐰",
    CharacterSpecies.PANDA: "🐼",
}


def generate_name(species: CharacterSpecies) -> str:
    """예: '고결한 파랑', '깡총 토토'."""
    rng = secrets.SystemRandom()
    adj = rng.choice(ADJECTIVES)
    nick = rng.choice(SPECIES_NICKNAMES[species])
    return f"{adj} {nick}"


def pick_species() -> CharacterSpecies:
    """5종 균등 추첨 (각 20%, v3)."""
    rng = secrets.SystemRandom()
    return rng.choice(
        [
            CharacterSpecies.TURTLE,
            CharacterSpecies.PENGUIN,
            CharacterSpecies.SQUIRREL,
            CharacterSpecies.RABBIT,
            CharacterSpecies.PANDA,
        ]
    )
