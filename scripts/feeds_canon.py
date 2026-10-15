"""Canonical feed-item URL (shared by feeds.py and edition.py): strip utm_* params and the fragment."""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
def canon(u):
    s = urlsplit(u.strip())
    q = [(k, v) for k, v in parse_qsl(s.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path, urlencode(q), ""))
