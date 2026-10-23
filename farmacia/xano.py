"""Server-side HTTP helpers for the DROGA-NONIMO Xano API."""

import os
from typing import Any

import httpx


XANO_API_URL = os.environ.get(
    "XANO_API_URL",
    "https://x8ki-letl-twmt.n7.xano.io/api:t7Ptjfi3",
).rstrip("/")
XANO_PHARMACY_API_URL = os.environ.get(
    "XANO_PHARMACY_API_URL",
    "https://x8ki-letl-twmt.n7.xano.io/api:M6el3Cg8",
).rstrip("/")


async def request(
    method: str,
    endpoint: str,
    *,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    auth_token: str = "",
    base_url: str | None = None,
) -> httpx.Response:
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    async with httpx.AsyncClient() as client:
        return await client.request(
            method,
            f"{(base_url or XANO_API_URL).rstrip('/')}/{endpoint.lstrip('/')}",
            params=params,
            json=payload,
            headers=headers,
            timeout=10.0,
        )


def response_data(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def response_message(data: Any, default: str) -> str:
    if isinstance(data, dict):
        message = data.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return default


def auth_token(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    token = data.get("authToken")
    return token.strip() if isinstance(token, str) else ""


def response_records(data: Any, resource: str) -> list[dict[str, Any]]:
    if not isinstance(data, list) or not all(
        isinstance(record, dict) for record in data
    ):
        raise ValueError(f"A resposta do Xano para {resource} não é uma lista válida.")
    return data
