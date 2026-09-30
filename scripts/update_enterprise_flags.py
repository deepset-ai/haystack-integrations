#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

"""
Sync the `enterprise` front-matter flag on Haystack Integrations pages.

Cross-references each integration page's `name` against the partner sections
of the Haystack Enterprise Platform components table, which is generated
nightly by deepset-ai/haystack's scripts/generate_platform_components_table.py
and published (publicly, no auth needed) at
docs-website/docs/overview/platform-components.mdx in that repo.

Any integration page whose `name` matches a partner section gets
`enterprise: true` in its front matter; pages that lose platform coverage
have the flag removed again.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PLATFORM_COMPONENTS_URL = (
    "https://raw.githubusercontent.com/deepset-ai/haystack/main/"
    "docs-website/docs/overview/platform-components.mdx"
)

# Platform partner section heading -> actual `name:` used on this repo's
# integration pages, for the handful of partners that don't match
# case-insensitively. Keep loosely in sync with PARTNER_LABELS in
# deepset-ai/haystack's scripts/generate_platform_components_table.py,
# which is what produces these section headings.
PARTNER_NAME_ALIASES: dict[str, str] = {
    "AIML API": "AIMLAPI",
    "Astra": "AstraDB",
    "Brave": "Brave Search",
    "Cometapi": "Comet API",
    "Edenai": "Eden AI",
    "Google Generative AI": "Google Gen AI",
    "MongoDB Atlas": "MongoDB",
    "Solr": "Apache Solr",
    "Tika": "Apache Tika",
    "Weights & Biases (Weave)": "Weights & Biases Weave Tracer",
    "Youcom": "You.com",
}

_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_NON_PARTNER_HEADINGS = {"Core Components", "Haystack Enterprise Components"}


def fetch_platform_partners(url: str) -> set[str]:
    """Return the set of partner section names from the platform components table."""
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - fixed, trusted public URL
        text = response.read().decode("utf-8")
    headings = {m.group(1).strip() for m in _HEADING_RE.finditer(text)}
    return headings - _NON_PARTNER_HEADINGS


def resolve_matches(partners: set[str], integration_names: set[str]) -> set[str]:
    """Return the subset of *integration_names* available on the Enterprise Platform."""
    names_lower = {n.lower(): n for n in integration_names}
    matched: set[str] = set()
    for partner in sorted(partners):
        candidate = PARTNER_NAME_ALIASES.get(partner, partner)
        resolved = names_lower.get(candidate.lower())
        if resolved:
            matched.add(resolved)
        else:
            logger.warning("No integration page found for platform partner: %s", partner)
    return matched


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    """Split *text* into (frontmatter_body, rest_of_file), or None if there's no front matter."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    body = text[3:end].strip("\n")
    rest = text[end + 4 :]
    return body, rest


def get_name(frontmatter_body: str) -> str | None:
    for line in frontmatter_body.splitlines():
        if line.startswith("name:"):
            return line[len("name:") :].strip().strip('"')
    return None


def set_enterprise_flag(frontmatter_body: str, enterprise: bool) -> tuple[str, bool]:
    """Return (new_frontmatter_body, changed)."""
    lines = frontmatter_body.splitlines()
    existing_idx = next((i for i, line in enumerate(lines) if line.startswith("enterprise:")), None)

    if enterprise:
        if existing_idx is not None:
            if lines[existing_idx].strip() == "enterprise: true":
                return frontmatter_body, False
            lines[existing_idx] = "enterprise: true"
        else:
            lines.append("enterprise: true")
        return "\n".join(lines), True

    if existing_idx is not None:
        del lines[existing_idx]
        return "\n".join(lines), True
    return frontmatter_body, False


def load_integrations(integrations_dir: Path) -> dict[Path, tuple[str, str, str]]:
    """Return {path: (name, frontmatter_body, rest_of_file)} for every parseable page."""
    result: dict[Path, tuple[str, str, str]] = {}
    for md_file in sorted(integrations_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            continue
        body, rest = parsed
        name = get_name(body)
        if name is None:
            continue
        result[md_file] = (name, body, rest)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--integrations-dir",
        type=Path,
        default=Path("integrations"),
        metavar="PATH",
        help="Directory containing integration .md pages (default: ./integrations).",
    )
    parser.add_argument(
        "--platform-components-url",
        default=PLATFORM_COMPONENTS_URL,
        metavar="URL",
        help="URL of the platform-components.mdx file to fetch.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing any files.",
    )
    args = parser.parse_args(argv)

    if not args.integrations_dir.is_dir():
        print(f"ERROR: --integrations-dir does not exist: {args.integrations_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        partners = fetch_platform_partners(args.platform_components_url)
    except OSError as exc:
        print(f"ERROR: could not fetch platform components table: {exc}", file=sys.stderr)
        sys.exit(1)

    logger.info("Found %d partner sections in the platform components table", len(partners))

    entries = load_integrations(args.integrations_dir)
    integration_names = {name for name, _, _ in entries.values()}
    enterprise_names = resolve_matches(partners, integration_names)
    logger.info("Matched %d integration page(s) to Enterprise Platform partners", len(enterprise_names))

    changed: list[tuple[Path, bool]] = []
    for md_file, (name, body, rest) in entries.items():
        should_be_enterprise = name in enterprise_names
        new_body, did_change = set_enterprise_flag(body, should_be_enterprise)
        if not did_change:
            continue
        changed.append((md_file, should_be_enterprise))
        if not args.dry_run:
            md_file.write_text(f"---\n{new_body}\n---{rest}", encoding="utf-8")

    for md_file, should_be_enterprise in changed:
        logger.info("%s: enterprise -> %s", md_file.name, should_be_enterprise)

    logger.info("%s %d file(s)", "Would update" if args.dry_run else "Updated", len(changed))


if __name__ == "__main__":
    main()
