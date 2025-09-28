import httpx

from magent.domain.meta import (
    RecommendationCriteria,
    AudioFeatures,
    Track,
    Artist, MusicServiceId,
)
from magent.domain.repository import RecommendationRepository

"""
https://reccobeats.com/docs/apis/reccobeats-api
"""
BASE_URL = "https://api.reccobeats.com"

SERVICE = "reccobeats"


class ReccobeatsRecommendationRepository(RecommendationRepository):
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    async def recommend(
        self,
        criteria: RecommendationCriteria,
        audio_features: AudioFeatures | None = None,
    ) -> list[Track]:
        criteria_params = criteria.model_dump(exclude_none=True, by_alias=True)
        audio_features = (
            audio_features.model_dump(exclude_none=True) if audio_features else {}
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/track/recommendation",
                params=criteria_params | audio_features,
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            Track(
                id=MusicServiceId(id=t["id"], service=SERVICE),
                title=t["trackTitle"],
                artists=[
                    Artist(
                        id=MusicServiceId(id=artist["id"], service=SERVICE),
                        name=artist["name"],
                    )
                    for artist in t["artists"]
                ],
                url=t["href"],
            )
            for t in data["content"]
        ]
