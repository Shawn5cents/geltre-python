# Agent Handoff

This is the public Python client SDK for the proprietary hosted Geltre service.

Rules:
- Keep this repository client-only.
- Never copy model weights, training code, private benchmark data, feature weights, production database files, API keys, or other secrets from the private Geltre repository.
- Preserve the public API contract documented at https://docs.nicholsai.com/.
- Keep runtime dependencies at zero unless a concrete user-facing requirement justifies adding one.
- Run `pytest -q` before merging.
- Benchmark/product claims must remain scoped to published Nichols AI evidence.
