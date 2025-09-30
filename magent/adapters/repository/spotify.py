import base64
import time
from functools import wraps
from typing import Callable, Awaitable

import httpx

from magent.domain.meta import Artist, Track, Query, MusicServiceId
from magent.domain.repository import ArtistRepository

"""
https://developer.spotify.com/documentation/web-api
"""
SERVICE = "spotify"
BASE_URL = "https://api.spotify.com"
MARKET = "KR"


class SpotifyAuth:
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.expires_at = 0

    async def get_token(self) -> str:
        if not self.token or self.is_expired():
            self.token, self.expires_at = await self._fetch_token()
        return self.token

    async def is_expired(self):
        return time.time() >= self.expires_at

    async def _fetch_token(self) -> tuple[str, float]:
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://accounts.spotify.com/api/token",
                headers={"Authorization": f"Basic {auth}"},
                data={"grant_type": "client_credentials"},
            )
        resp.raise_for_status()
        data = resp.json()
        return data["access_token"], time.time() + data["expires_in"] - 30

    async def get_auth_header(self) -> dict[str, str]:
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}


def with_auth(func: Callable[..., Awaitable]):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        headers = await self.auth.get_auth_header()
        kwargs["headers"] = {**kwargs.get("headers", {}), **headers}
        return await func(self, *args, **kwargs)

    return wrapper


class SpotifySearchRepository:
    def __init__(self, client_id: str, client_secret: str):
        self.auth = SpotifyAuth(client_id, client_secret)

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

    def __init__(self, client_id: str, client_secret: str):
        self.auth = SpotifyAuth(client_id, client_secret)
        self.search_repo = SpotifySearchRepository(client_id, client_secret)

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
