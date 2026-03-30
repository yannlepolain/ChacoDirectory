#!/usr/bin/env python3
"""
Fetch researcher webpages and flag likely profile mismatches.

This script uses live network requests. It is intended to catch cases where a
stored webpage points to the wrong person, such as a mismatched ORCID page.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import socket
import ssl
import sys
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlparse, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"
USER_AGENT = "ChacoMap webpage audit/1.0"
DEFAULT_TIMEOUT = 15.0
DEFAULT_WORKERS = 8

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class WebpageResult:
    name: str
    url: str
    final_url: str
    status: int | None
    error: str
    title: str
    score: int
    reasons: tuple[str, ...]


def load_dataset() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return WHITESPACE_RE.sub(" ", text.lower()).strip()


def encode_url(url: str) -> str:
    parts = urlsplit(url)
    path = quote(parts.path, safe="/:@")
    query = quote(parts.query, safe="=&?/:@,+%")
    fragment = quote(parts.fragment, safe="")
    return urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


def name_tokens(name: str) -> tuple[list[str], list[str]]:
    surname, _, given = name.partition(",")
    surname_tokens = [token for token in re.split(r"[\s\-]+", normalize(surname)) if len(token) >= 3]
    given_tokens = [token for token in re.split(r"[\s\-]+", normalize(given)) if len(token) >= 3]
    return surname_tokens, given_tokens


def fetch_page(url: str, timeout: float) -> tuple[int | None, str, str, str]:
    request = urllib.request.Request(encode_url(url), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            final_url = response.geturl()
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read().decode(charset, errors="replace")
            return status, final_url, body, ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl() or url, "", f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            return None, url, "", "timeout"
        if isinstance(reason, ssl.SSLError):
            return None, url, "", f"ssl error: {reason}"
        return None, url, "", str(reason)
    except TimeoutError:
        return None, url, "", "timeout"
    except Exception as exc:  # pragma: no cover - defensive fallback
        return None, url, "", str(exc)


def extract_text(body: str) -> tuple[str, str]:
    title_match = TITLE_RE.search(body)
    title = html.unescape(title_match.group(1)).strip() if title_match else ""
    text = html.unescape(TAG_RE.sub(" ", body))
    text = WHITESPACE_RE.sub(" ", text).strip()
    return title, text


def fetch_orcid_name(orcid_url: str, timeout: float) -> tuple[str, str]:
    orcid_id = urlparse(orcid_url).path.strip("/")
    api_url = f"https://pub.orcid.org/v3.0/{orcid_id}/personal-details"
    request = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        payload = json.loads(response.read().decode(charset, errors="replace"))
    given = (((payload.get("name") or {}).get("given-names") or {}).get("value") or "").strip()
    family = (((payload.get("name") or {}).get("family-name") or {}).get("value") or "").strip()
    return given, family


def audit_webpage(name: str, url: str, timeout: float) -> WebpageResult:
    source_domain = urlparse(url).netloc.lower()
    if "orcid.org" in source_domain:
        try:
            given, family = fetch_orcid_name(url, timeout)
            page_identity = normalize(f"{family}, {given}")
            expected_identity = normalize(name)
            score = 0
            reasons: list[str] = []
            if page_identity != expected_identity:
                score = 8
                reasons.append(f"ORCID profile is for '{family}, {given}'")
            return WebpageResult(
                name=name,
                url=url,
                final_url=url,
                status=200,
                error="",
                title=f"ORCID: {family}, {given}".strip(),
                score=score,
                reasons=tuple(reasons),
            )
        except Exception as exc:
            return WebpageResult(name, url, url, None, str(exc), "", 10, (str(exc),))

    status, final_url, body, error = fetch_page(url, timeout)
    if error:
        return WebpageResult(name, url, final_url, status, error, "", 10, (error,))

    title, text = extract_text(body)
    haystack = normalize(f"{title} {text[:6000]}")
    surnames, givens = name_tokens(name)
    reasons: list[str] = []
    score = 0

    surname_hit = any(token in haystack for token in surnames)
    given_hit = any(token in haystack for token in givens)

    if not surname_hit:
        score += 5
        reasons.append("surname not found in page content")
    if not given_hit:
        score += 3
        reasons.append("given name not found in page content")

    final_domain = urlparse(final_url).netloc.lower()
    if final_domain != source_domain:
        score += 1
        reasons.append(f"redirected to {final_domain or final_url}")

    if "orcid.org" in source_domain and not (surname_hit and given_hit):
        score += 3
        reasons.append("ORCID page content does not match stored researcher name")

    return WebpageResult(name, url, final_url, status, "", title, score, tuple(reasons))


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--max-report", type=int, default=100)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    researchers = load_dataset()
    webpages = [(r["name"], (r.get("webpage") or "").strip()) for r in researchers if (r.get("webpage") or "").strip()]

    results: list[WebpageResult] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(audit_webpage, name, url, args.timeout) for name, url in webpages]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda result: (-result.score, result.name))

    print(f"Dataset: {DATA_PATH}")
    print(f"Researcher webpages checked: {len(results)}")

    flagged = [result for result in results if result.score >= args.min_score]
    print(f"Flagged webpages: {len(flagged)}")

    for result in flagged[: max(1, args.max_report)]:
        status = result.status if result.status is not None else "-"
        print(f"- score={result.score} | {result.name}")
        print(f"  url={result.url}")
        print(f"  status={status}")
        if result.final_url and result.final_url != result.url:
            print(f"  final_url={result.final_url}")
        if result.title:
            print(f"  title={result.title}")
        for reason in result.reasons:
            print(f"  reason={reason}")

    if len(flagged) > args.max_report:
        print(f"... {len(flagged) - args.max_report} additional flagged webpages omitted")

    return 0 if not flagged else 1


if __name__ == "__main__":
    raise SystemExit(main())
