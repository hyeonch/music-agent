from abc import ABC, abstractmethod

from magent.domain.meta import Artist, Track, RecommendationCriteria, AudioFeatures


class ArtistRepository(ABC):
    @abstractmethod
    async def search_artist(self, name: str) -> Artist:
        raise NotImplementedError
    
    @abstractmethod
    async def get_artist_top_tracks(self, artist: Artist) -> list[Track]:
        raise NotImplementedError


class RecommendationRepository(ABC):
    @abstractmethod
    async def recommend(
        self,
        criteria: RecommendationCriteria,
        audio_features: AudioFeatures | None = None,
    ) -> list[Track]:
        raise NotImplementedError
