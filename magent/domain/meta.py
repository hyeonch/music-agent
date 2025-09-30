from typing import Literal

from pydantic import BaseModel, Field


class MusicServiceId(BaseModel):
    id: str
    service: Literal["spotify", "reccobeats", "musicbrainz"]

class Artist(BaseModel):
    id: MusicServiceId
    name: str


class Track(BaseModel):
    id: MusicServiceId
    title: str
    artists: list[Artist]
    url: str


class Query(BaseModel):
    keyword: str | None = None
    album: str | None = None
    artist: str | None = None
    track: str | None = None
    year: str | None = None  # "1999" or "1990-2000"
    upc: str | None = None
    isrc: str | None = None
    genre: str | None = None
    tag_new: bool = False
    tag_hipster: bool = False

    def build(self) -> str:
        parts = []
        if self.keyword:
            parts.append(self.keyword)
        if self.album:
            parts.append(f"album:{self.album}")
        if self.artist:
            parts.append(f"artist:{self.artist}")
        if self.track:
            parts.append(f"track:{self.track}")
        if self.year:
            parts.append(f"year:{self.year}")
        if self.upc:
            parts.append(f"upc:{self.upc}")
        if self.isrc:
            parts.append(f"isrc:{self.isrc}")
        if self.genre:
            parts.append(f"genre:{self.genre}")
        if self.tag_new:
            parts.append("tag:new")
        if self.tag_hipster:
            parts.append("tag:hipster")

        return " ".join(parts)


class AudioFeatures(BaseModel):
    acousticness: float | None = None
    danceability: float | None = None
    energy: float | None = None
    instrumentalness: float | None = None
    liveness: float | None = None
    loudness: float | None = None
    speechiness: float | None = None
    valence: float | None = None


class RecommendationCriteria(BaseModel):
    size: int
    seeds: list[str]
    negative_seeds: list[str] | None = Field(None, alias="negativeSeeds")
    popularity: int | None = None
    feature_weight: float | None = Field(None, alias="featureWeight")

