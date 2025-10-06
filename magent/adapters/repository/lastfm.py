import httpx

from magent.domain.meta import Artist, MusicServiceId, Track
from magent.domain.repository import TrackRepository

from magent.service.trace.tracer import trace

"""
https://www.last.fm/api
"""

SERVICE = "musicbrainz"
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFmTrackRepository(TrackRepository):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @trace(name="repo.lastfm.search_track", as_type="tool")
    async def search_track(self, title: str, artist: str | None = None) -> Track:
        params = {
            "method": "track.search",
            "api_key": self.api_key,
            "track": title,
            "artist": artist or "",
            "format": "json",
            "limit": 100,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        track_matches = data.get("results", {}).get("trackmatches", {}).get("track", [])
        for item in track_matches:
            artist_data = item.get("artist", "")
            if not artist_data or not (track_mbid := item.get("mbid")):
                continue

            artist = Artist(id=MusicServiceId(id="", service=SERVICE), name=artist_data)
            track = Track(
                id=MusicServiceId(id=track_mbid, service=SERVICE),
                artists=[artist],
                title=item.get("name"),
                url=item.get("url"),
            )
            return track

    @trace(name="repo.lastfm.get_similar_tracks", as_type="tool")
    async def get_similar_tracks(self, track: Track, limit: int = 10) -> list[Track]:
        params = {
            "method": "track.getsimilar",
            "api_key": self.api_key,
            "format": "json",
            "limit": limit,
        }
        if track.id.service == SERVICE and track.id.id:
            params |= {"mbid": track.id.id}
        else:
            params |= {"artist": track.artists[0].name, "track": track.title}

        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        similar_tracks = data.get("similartracks", {}).get("track", [])
        result = []
        for item in similar_tracks:
            artist_data = item.get("artist", {})

            if not (artist_mbid := artist_data.get("mbid")) or not (
                track_mbid := item.get("mbid")
            ):
                continue

            artist = Artist(
                id=MusicServiceId(id=artist_mbid, service=SERVICE),
                name=artist_data.get("name"),
            )
            track = Track(
                id=MusicServiceId(id=track_mbid, service=SERVICE),
                artists=[artist],
                title=item.get("name"),
                url=item.get("url"),
            )
            result.append(track)
        return result
