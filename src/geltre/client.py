from __future__ import annotations

import json
import os
import uuid
import urllib.error
import urllib.request
from typing import Any, Callable

DEFAULT_BASE_URL = "https://api.nicholsai.com"


class GeltreError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None):
        super().__init__(message)
        self.status = status


class AuthenticationError(GeltreError):
    pass


class PaymentRequiredError(GeltreError):
    pass


class ConflictError(GeltreError):
    pass


def _error_for_status(status: int, message: str) -> GeltreError:
    if status == 401:
        return AuthenticationError(message, status=status)
    if status == 402:
        return PaymentRequiredError(message, status=status)
    if status == 409:
        return ConflictError(message, status=status)
    return GeltreError(message, status=status)


class Geltre:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        opener: Callable[..., Any] | None = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._opener = opener or urllib.request.urlopen
        self.timeout = timeout

    @classmethod
    def from_env(cls, **kwargs: Any) -> "Geltre":
        key = os.environ.get("GELTRE_API_KEY")
        if not key:
            raise AuthenticationError("GELTRE_API_KEY is not set")
        return cls(key, **kwargs)

    @classmethod
    def claim_invite(
        cls,
        invite_code: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        opener: Callable[..., Any] | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        client = cls(base_url=base_url, opener=opener, timeout=timeout)
        return client._request(
            "POST",
            "/v1/developer/claim",
            payload={"invite_code": invite_code},
            authenticated=False,
        )

    def billing_status(self) -> dict[str, Any]:
        return self._request("GET", "/v1/billing/status", authenticated=False)

    def balance(self) -> dict[str, Any]:
        return self._request("GET", "/v1/balance")

    def orient(
        self,
        *,
        task: str,
        state: list[dict[str, Any]],
        budget: int = 5,
        target: str = "decision",
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        key = idempotency_key or f"req_{uuid.uuid4().hex}"
        return self._request(
            "POST",
            "/v1/orient",
            payload={
                "task": task,
                "state": state,
                "budget": budget,
                "target": target,
            },
            headers={"Idempotency-Key": key},
        )

    def create_checkout(self, *, credit_cents: int) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/billing/checkout",
            payload={"credit_cents": credit_cents},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        request_headers = {
            "Accept": "application/json",
            "User-Agent": "geltre-python/0.1.0",
            **(headers or {}),
        }
        if authenticated:
            if not self.api_key:
                raise AuthenticationError("Geltre API key is required")
            request_headers["Authorization"] = f"Bearer {self.api_key}"

        body = None
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            with self._opener(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(raw).get("error") or f"HTTP {exc.code}"
            except json.JSONDecodeError:
                message = f"HTTP {exc.code}"
            raise _error_for_status(exc.code, message) from None
        except urllib.error.URLError as exc:
            raise GeltreError(f"network error: {exc.reason}") from None
