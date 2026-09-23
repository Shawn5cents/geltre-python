# Geltre Python SDK

Official Python client for **Geltre**, the Orienting Model by [Nichols AI](https://nicholsai.com/#geltre).

> Geltre selects what matters before AI decides what to do.

This repository contains **client SDK code only**. The Geltre model, weights, training system, private datasets, and production inference implementation are proprietary and are not included here.

## Install

Until the first PyPI release is published:

```bash
pip install "git+https://github.com/Shawn5cents/geltre-python.git"
```

Python 3.10+ is supported. The runtime SDK has no third-party dependencies.

## Quick start

Set the API key issued by the [Geltre Console](https://console.nicholsai.com/):

```bash
export GELTRE_API_KEY="gt_test_..."
```

Then orient state:

```python
from geltre import Geltre

client = Geltre.from_env()

result = client.orient(
    task="Determine whether the target service should restart after failure",
    state=[
        {
            "ref": "context:1",
            "source": "context",
            "text": "target service expected mode running; restart policy on failure",
        },
        {
            "ref": "context:2",
            "source": "context",
            "text": "target service failed after the latest start attempt",
        },
        {"ref": "status:1", "source": "status", "text": "unit status exit code 1"},
        {
            "ref": "meta:1",
            "source": "meta",
            "text": "distractor service backup completed successfully",
        },
    ],
    budget=2,
)

print(result["evidence"])
```

## Developer preview invite

Approved preview developers can claim a one-time invite:

```python
from geltre import Geltre

claim = Geltre.claim_invite("gti_...")
print(claim["api_key"])  # store securely; shown once
```

The current preview grants $1 of promotional credit to approved invite claims.

## API surface

- `Geltre.orient(...)`
- `Geltre.balance()`
- `Geltre.billing_status()`
- `Geltre.create_checkout(...)`
- `Geltre.claim_invite(...)`
- `Geltre.from_env()`

Full API and benchmark documentation: https://docs.nicholsai.com/introduction/

## Preview scope

The hosted developer preview is currently scoped to the validated ServiceOps selector. Nichols AI does **not** claim universal cross-domain robustness. Public benchmark docs include the negative CodeOps cross-distribution result.

## Development

```bash
python -m pip install -e ".[test]"
pytest -q
```

## License

The SDK source in this repository is MIT licensed.

The hosted Geltre model and related proprietary model assets are **not** licensed under MIT and are not distributed in this repository.
