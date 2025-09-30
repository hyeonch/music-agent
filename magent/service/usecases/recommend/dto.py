from typing import Self

from pydantic import BaseModel

from magent.domain.meta import Track


class RecommendByArtistRequest(BaseModel):
    artist_name: str
    limit: int = 10


class RecommendByTrackRequest(BaseModel):
    artist_name: str | None = None
    track_title: str
    limit: int = 10


class TrackDto(BaseModel):
    title: str
    artists: list[str]

    @classmethod
    def from_domain(cls, track: Track) -> Self:
        return cls(
            title=track.title,
            artists=[artist.name for artist in track.artists],
        )


class RecommendResponse(BaseModel):
    tracks: list[TrackDto]
