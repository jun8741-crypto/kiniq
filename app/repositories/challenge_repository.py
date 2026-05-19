from datetime import date

from app.models.challenge import Challenge, ChallengeTrack, UserChallenge, UserChallengeStatus


class ChallengeRepository:
    async def list_by_track(self, track: ChallengeTrack) -> list[Challenge]:
        return await Challenge.filter(track=track, is_active=True)

    async def get_by_id(self, challenge_id: int) -> Challenge | None:
        return await Challenge.get_or_none(id=challenge_id, is_active=True)


class UserChallengeRepository:
    async def get_active(self, user_id: int, challenge_id: int) -> UserChallenge | None:
        return await UserChallenge.get_or_none(user_id=user_id, challenge_id=challenge_id)

    async def create(self, user_id: int, challenge_id: int, started_at: date) -> UserChallenge:
        return await UserChallenge.create(
            user_id=user_id,
            challenge_id=challenge_id,
            started_at=started_at,
        )

    async def list_by_user(
        self,
        user_id: int,
        status: UserChallengeStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, list[UserChallenge]]:
        qs = UserChallenge.filter(user_id=user_id)
        if status is not None:
            qs = qs.filter(status=status)
        total = await qs.count()
        items = await qs.order_by("-created_at").offset(offset).limit(limit)
        return total, items

    async def get_by_id(self, user_challenge_id: int, user_id: int) -> UserChallenge | None:
        return await UserChallenge.get_or_none(id=user_challenge_id, user_id=user_id)

    async def save(self, user_challenge: UserChallenge) -> None:
        await user_challenge.save()
