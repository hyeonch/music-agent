import base64
import time

import httpx


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
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
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