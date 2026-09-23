import json
import urllib.error
from io import BytesIO

import pytest

from geltre import AuthenticationError, ConflictError, Geltre


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def opener_for(payload, *, capture=None):
    def opener(request, timeout=30):
        if capture is not None:
            capture["request"] = request
            capture["timeout"] = timeout
        return FakeResponse(payload)
    return opener


def test_orient_builds_authenticated_request():
    capture = {}
    client = Geltre(
        "gt_test_fixture_key",
        opener=opener_for(
            {
                "evidence": [{"ref": "context:2", "relevance": 0.99}],
                "model": "geltre-serviceops-linear-v03",
                "usage": {"input_tokens": 12, "charged_microcents": 60},
            },
            capture=capture,
        ),
    )

    result = client.orient(
        task="Determine whether the target service should restart after failure",
        state=[
            {
                "ref": "context:2",
                "source": "context",
                "text": "target service failed after the latest start attempt",
            }
        ],
        budget=1,
        idempotency_key="req_fixture",
    )

    request = capture["request"]
    assert request.full_url.endswith("/v1/orient")
    assert request.get_header("Authorization") == "Bearer gt_test_fixture_key"
    assert request.get_header("Idempotency-key") == "req_fixture"
    assert result["evidence"][0]["ref"] == "context:2"


def test_claim_invite_is_unauthenticated():
    capture = {}
    result = Geltre.claim_invite(
        "gti_fixture",
        opener=opener_for(
            {
                "customer_id": "cus_fixture",
                "api_key": "gt_test_fixture_key",
                "promo_credit_cents": 100,
                "balance_microcents": 100_000_000,
            },
            capture=capture,
        ),
    )
    assert capture["request"].get_header("Authorization") is None
    assert result["promo_credit_cents"] == 100


def test_missing_api_key_fails_before_network():
    client = Geltre()
    with pytest.raises(AuthenticationError):
        client.balance()


def test_http_409_maps_to_conflict():
    def opener(request, timeout=30):
        fp = BytesIO(b'{"error":"developer invite already claimed"}')
        raise urllib.error.HTTPError(
            request.full_url,
            409,
            "Conflict",
            {},
            fp,
        )

    client = Geltre("gt_test_fixture_key", opener=opener)
    with pytest.raises(ConflictError, match="already claimed"):
        client.balance()
