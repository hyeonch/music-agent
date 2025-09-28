from functools import wraps
from typing import Callable, Awaitable

import httpx

from magent.domain.meta import Artist, Track, Query, MusicServiceId
from magent.domain.repository import ArtistRepository
from magent.infra.spotify import SpotifyAuth

"""
https://developer.spotify.com/documentation/web-api
"""
SERVICE = "spotify"
BASE_URL = "https://api.spotify.com"
MARKET = "KR"


def with_auth(func: Callable[..., Awaitable]):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        headers = await self.auth.get_auth_header()
        kwargs["headers"] = {**kwargs.get("headers", {}), **headers}
        return await func(self, *args, **kwargs)

    return wrapper


class SpotifySearchRepository:
    def __init__(self, auth: SpotifyAuth):
        self.auth = auth

    @with_auth
    async def search(
        self, query: Query, type_: str, limit: int = 10, headers: dict = None
    ) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v1/search",
                params={
                    "q": query.build(),
                    "type": type_,
                    "market": MARKET,
                    "limit": limit,
                },
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        return data


class SpotifyArtistRepository(ArtistRepository):
    type_ = "artist"

    def __init__(self, auth: SpotifyAuth):
        self.auth = auth
        self.search_repo = SpotifySearchRepository(auth)

    async def search_artist(self, name: str) -> Artist:
        results = await self.search_repo.search(
            Query(keyword=name), self.type_, limit=10
        )
        item = results["artists"]["items"][0]
        return Artist(
            id=MusicServiceId(id=item["id"], service=SERVICE), name=item["name"]
        )

    @with_auth
    async def get_artist_top_tracks(
        self, artist: Artist, headers: dict = None
    ) -> list[Track]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/v1/artists/{artist.id.id}/top-tracks",
                params={"market": MARKET},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            Track(
                id=MusicServiceId(id=t["id"], service=SERVICE),
                title=t["name"],
                artists=[
                    Artist(
                        id=MusicServiceId(id=a["id"], service=SERVICE),
                        name=a["name"],
                    )
                    for a in t["artists"]
                ],
                url=t["external_urls"]["spotify"],
            )
            for t in data["tracks"]
        ]
