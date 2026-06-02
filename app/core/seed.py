"""
챌린지 시드 데이터 자동 삽입 — FastAPI lifespan에서 호출.
이미 존재하는 항목은 건너뜀 (멱등).
"""

import json
from pathlib import Path

_DATA_FILE = Path(__file__).parent.parent.parent / "src" / "ckd" / "data" / "challenges_v04.json"


async def seed_challenges() -> None:
    from app.models.challenge import Challenge, ChallengeCategory, ChallengeTrack

    if not _DATA_FILE.exists():
        print("[seed] challenges_v04.json 없음 — 건너뜀")
        return

    challenges = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    inserted = 0
    for item in challenges:
        exists = await Challenge.filter(
            name=item["name"],
            track=ChallengeTrack(item["track"]),
            stage=item["stage"],
        ).exists()
        if exists:
            continue
        await Challenge.create(
            name=item["name"],
            category=ChallengeCategory(item["category"]),
            description=item["description"],
            duration_days=item["duration_days"],
            track=ChallengeTrack(item["track"]),
            stage=item["stage"],
        )
        inserted += 1

    if inserted:
        print(f"[seed] 챌린지 {inserted}건 삽입 완료")
