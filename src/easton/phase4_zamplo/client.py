"""
Zamplo API client.

Zamplo's public API contract isn't published — confirm exact endpoint paths,
auth header format, and request/response shapes with Zamplo support before
filling in the methods below.

Skeleton uses httpx + bearer-token auth which is the common pattern. Adjust
once Zamplo confirms.
"""

from __future__ import annotations

import os
import logging

import httpx

log = logging.getLogger(__name__)


class ZamploClient:
    """Thin wrapper over Zamplo's REST API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.environ["ZAMPLO_API_KEY"]
        self.base_url = base_url or os.environ.get(
            "ZAMPLO_API_BASE_URL", "https://data.zamplo.com/api/v1"
        )
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    # ---- Endpoints — replace with real paths after confirming with Zamplo ----

    def lookup_by_parcel(self, state: str, county: str, parcel_id: str) -> dict:
        """
        Look up one parcel by state + county + parcel ID.

        TODO: confirm endpoint path. Likely something like:
            GET /parcels?state={state}&county={county}&apn={parcel_id}
        """
        raise NotImplementedError("Confirm endpoint with Zamplo support.")

    def lookup_by_owner(self, state: str, owner_name: str) -> list[dict]:
        """
        Look up parcels by owner name in a state.

        TODO: confirm endpoint path.
        """
        raise NotImplementedError("Confirm endpoint with Zamplo support.")

    def batch_enrich(self, parcel_ids: list[dict]) -> list[dict]:
        """
        Batch-enrich a list of parcels. Many platforms offer a /batch endpoint
        that's significantly cheaper per-row than individual calls.

        TODO: confirm whether Zamplo supports batch and what the limit is.
        """
        raise NotImplementedError("Confirm endpoint with Zamplo support.")

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
