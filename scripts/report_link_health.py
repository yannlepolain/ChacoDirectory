#!/usr/bin/env python3
"""
Check live health of publication URLs, DOI resolvers, and researcher webpages.

This script uses live network requests. It is intended to be run manually when
doing a trust audit of external links.
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"
USER_AGENT = "ChacoMap link audit/1.0"
DEFAULT_TIMEOUT = 15.0
DEFAULT_WORKERS = 8


@dataclass(frozen=True)
class Target:
    kind: str
    owner: str
    label: str
    url: str


@dataclass(frozen=True)
class Result:
    target: Target
    ok: bool
    status: int | None
    final_url: str
    error: str


def load_dataset() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def encode_url(url: str) -> str:
    parts = urlsplit(url)
    path = quote(parts.path, safe="/:@")
    query = quote(parts.query, safe="=&?/:@,+%")
    fragment = quote(parts.fragment, safe="")
    return urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


def build_targets(
    researchers: list[dict],
    include_publications: bool,
    include_dois: bool,
    include_webpages: bool,
) -> list[Target]:
    targets: list[Target] = []

    for researcher in researchers:
        name = researcher["name"]

        if include_webpages:
            webpage = (researcher.get("webpage") or "").strip()
            if webpage:
                targets.append(Target("webpage", name, "researcher webpage", webpage))

        if not include_publications and not include_dois:
            continue

        for publication in researcher.get("publications", []):
            title = publication.get("title", "")
            url = (publication.get("url") or "").strip()
            doi = (publication.get("doi") or "").strip()

            if include_publications and url:
                targets.append(Target("publication_url", name, title, url))

            if include_dois and doi:
                targets.append(Target("doi", name, title, f"https://doi.org/{doi}"))

    return targets


def fetch_url(url: str, timeout: float) -> tuple[int | None, str, str]:
    request = urllib.request.Request(encode_url(url), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            final_url = response.geturl()
            return status, final_url, ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl() or url, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.timeout):
            return None, url, "timeout"
        if isinstance(reason, ssl.SSLError):
            return None, url, f"ssl error: {reason}"
        return None, url, str(reason)
    except TimeoutError:
        return None, url, "timeout"
    except Exception as exc:  # pragma: no cover - defensive fallback
        return None, url, str(exc)


def check_target(target: Target, timeout: float) -> Result:
    status, final_url, error = fetch_url(target.url, timeout)
    ok = error == "" and status is not None and 200 <= status < 400
    return Result(target, ok, status, final_url, error)


def summarize(results: list[Result], max_report: int) -> int:
    broken = [result for result in results if not result.ok]
    redirected = [
        result
        for result in results
        if result.ok and result.final_url.rstrip("/") != result.target.url.rstrip("/")
    ]

    print(f"Dataset: {DATA_PATH}")
    print(f"Targets checked: {len(results)}")
    print(f"Healthy: {len(results) - len(broken)}")
    print(f"Broken or unreachable: {len(broken)}")
    print(f"Redirected: {len(redirected)}")

    if broken:
        print("\nBroken or unreachable targets:")
        for result in broken[:max_report]:
            status = result.status if result.status is not None else "-"
            print(
                f"- [{result.target.kind}] {result.target.owner} | {result.target.label}\n"
                f"  url={result.target.url}\n"
                f"  status={status} error={result.error}"
            )
        if len(broken) > max_report:
            print(f"... {len(broken) - max_report} additional broken targets omitted")

    if redirected:
        print("\nRedirected targets:")
        for result in redirected[:max_report]:
            print(
                f"- [{result.target.kind}] {result.target.owner} | {result.target.label}\n"
                f"  from={result.target.url}\n"
                f"  to={result.final_url}"
            )
        if len(redirected) > max_report:
            print(f"... {len(redirected) - max_report} additional redirected targets omitted")

    return 0 if not broken else 1


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--max-report", type=int, default=100)
    parser.add_argument("--no-publications", action="store_true")
    parser.add_argument("--no-dois", action="store_true")
    parser.add_argument("--include-webpages", action="store_true")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    researchers = load_dataset()
    targets = build_targets(
        researchers,
        include_publications=not args.no_publications,
        include_dois=not args.no_dois,
        include_webpages=args.include_webpages,
    )

    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [executor.submit(check_target, target, args.timeout) for target in targets]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda result: (result.target.kind, result.target.owner, result.target.label))
    return summarize(results, max_report=max(1, args.max_report))


if __name__ == "__main__":
    raise SystemExit(main())
