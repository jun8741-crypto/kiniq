"""
챌린지 시드 데이터 삽입 스크립트.

Usage:
    python -m src.ckd.seed              # 중복 건너뜀 (기본)
    python -m src.ckd.seed --truncate   # 기존 데이터 삭제 후 재삽입
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from tortoise import Tortoise

_DATA_FILE = Path(__file__).parent / "data" / "challenges_v04.json"


async def seed(truncate: bool = False) -> None:
    from app.core.db.databases import TORTOISE_ORM
    from app.models.challenge import Challenge, ChallengeCategory, ChallengeTrack

    await Tortoise.init(config=TORTOISE_ORM)

    challenges = json.loads(_DATA_FILE.read_text(encoding="utf-8"))

    if truncate:
        deleted = await Challenge.all().delete()
        print(f"기존 챌린지 {deleted}건 삭제.")

    inserted = 0
    skipped = 0
    for item in challenges:
        exists = await Challenge.filter(
            name=item["name"],
            track=ChallengeTrack(item["track"]),
            stage=item["stage"],
        ).exists()
        if exists:
            skipped += 1
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

    await Tortoise.close_connections()
    print(f"완료 — 삽입: {inserted}건, 건너뜀: {skipped}건 (총 {len(challenges)}건)")


def main() -> None:
    parser = argparse.ArgumentParser(description="challenges 테이블 시드 삽입")
    parser.add_argument("--truncate", action="store_true", help="기존 데이터 삭제 후 재삽입")
    args = parser.parse_args()

    sys.exit(asyncio.run(seed(truncate=args.truncate)) or 0)


if __name__ == "__main__":
    main()
