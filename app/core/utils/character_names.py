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
}

SPECIES_EMOJI: dict[CharacterSpecies, str] = {
    CharacterSpecies.TURTLE: "🐢",
    CharacterSpecies.PENGUIN: "🐧",
    CharacterSpecies.SQUIRREL: "🐿️",
}


def generate_name(species: CharacterSpecies) -> str:
    """예: '고결한 파랑', '호기심 많은 차마'."""
    rng = secrets.SystemRandom()
    adj = rng.choice(ADJECTIVES)
    nick = rng.choice(SPECIES_NICKNAMES[species])
    return f"{adj} {nick}"


def pick_species() -> CharacterSpecies:
    """3종 균등 추첨 (각 33.33%)."""
    rng = secrets.SystemRandom()
    return rng.choice([CharacterSpecies.TURTLE, CharacterSpecies.PENGUIN, CharacterSpecies.SQUIRREL])
