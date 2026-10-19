#!/usr/bin/env python3
"""Live API smoke tests (no test mode). Run: GREIP_TOKEN=... python scripts/live_integration.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from greip.greip import Greip  # noqa: E402

TOKEN = os.environ.get("GREIP_TOKEN", "")
if not TOKEN:
    print("GREIP_TOKEN required", file=sys.stderr)
    sys.exit(1)

g = Greip(token=TOKEN, test_mode=False)
errors = []


def check(name, fn):
    try:
        fn()
        print(f"OK {name}")
    except Exception as e:
        errors.append(f"{name}: {e}")
        print(f"FAIL {name}: {e}")


def _ip_address(r):
    ip = getattr(r, "ip", None)
    if isinstance(ip, dict):
        return ip.get("address")
    return ip


check(
    "lookup",
    lambda: (_ := g.lookup("1.1.1.1")) and _ip_address(_) == "1.1.1.1",
)
check("threats", lambda: g.threats("1.1.1.1"))
check("bulk_lookup", lambda: g.bulk_lookup(["1.1.1.1", "8.8.8.8"]))
check("country", lambda: g.country("PS"))
check("asn", lambda: (_ := g.asn("AS13335")) and getattr(_, "number", None) == "AS13335")
check("email", lambda: g.email("name@domain.com"))
check("phone", lambda: g.phone("1234567890", "TR"))
check(
    "iban",
    lambda: (_ := g.iban("DE89370400440532013000")) and getattr(_, "is_valid", None) is True,
)
check(
    "profanity",
    lambda: (_ := g.profanity("This is a test message"))
    and getattr(_, "risk_level", None) == "low",
)
check(
    "payment",
    lambda: g.payment(
        {
            "action": "purchase",
            "website_domain": "greip.io",
            "transaction_amount": 1000,
            "transaction_currency": "GBP",
            "customer_email": "name@domain.com",
            "customer_ip": "1.1.1.1",
        }
    ),
)

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("All python live checks passed.")
