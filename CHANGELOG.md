# Changelog

## 2.0.0 — 2026-03-19

### Breaking

- **Greip API v2** (`https://v2.greipapi.com`) with Bearer authentication.
- Parses `success` / `data` envelope; raises on `success: false`.
- Routes and HTTP methods updated (e.g. `score/ip`, `lookup/countries`, POST profanity and payments).
- Response objects expose v2 field names (`is_valid`, nested `ip`, ASN `number`, `risk_level`).

### Added

- `scripts/live_integration.py` for live smoke tests (set `GREIP_TOKEN`).
