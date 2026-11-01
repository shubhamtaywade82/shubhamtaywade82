#!/usr/bin/env python3
"""Refresh the published-packages table in README.md from npm and RubyGems.

Versions and download counts come from the registries at run time. The
"what it does" copy is maintained here so the README stays hand-written prose.
Only the block between the packages markers is rewritten; everything else in
the README is left untouched.

Fails without writing anything if any registry lookup fails, so a partial
outage can never leave a half-updated table behind.
"""
import json
import os
import sys
import urllib.request

README = os.path.join(os.path.dirname(__file__), "..", "README.md")
START = "<!-- packages:start -->"
END = "<!-- packages:end -->"
USER_AGENT = "profile-package-sync"

# (npm name, description). Scoped names are looked up with the "/" encoded.
NPM = [
    ("@nemesis-oss/dhanhq-sdk", "TypeScript SDK for DhanHQ v2 — REST, WebSocket feed, option analytics, risk pipeline, MCP server"),
    ("@nemesis-oss/ollama-sdk", "TypeScript SDK for Ollama — native fetch, HA failover, tool calling, OpenAI/Anthropic bridges, MCP"),
    ("@nemesis-oss/binance-sdk", "Spot/USD-M/COIN-M Futures/Margin/Wallet, HMAC/Ed25519/RSA signing, MCP server"),
    ("@nemesis-oss/coindcx-sdk", "Spot/Margin/Futures for CoinDCX, local paper engine, MCP toolkits"),
    ("@nemesis-oss/agentic-runtime", "Model-agnostic autonomous agent runtime — Brain/Hands/Memory/Loop"),
    ("@nemesis-oss/devagent-ts", "Terminal coding-agent runtime, Docker sandbox, LSP intelligence *(legacy — successor is nexum)*"),
    ("@nemesis-oss/tg-format", "Type-safe Telegram formatting — native entities, HTML and MarkdownV2 from one message model"),
    ("@nemesis-oss/termina-core", "Ink 8 fork — terminal rendering engine with reflow-aware resize, mouse, OSC 8/52"),
    ("@nemesis-oss/termina-ui", "Ink-UI 2 fork — component kit on termina-core, grapheme-correct text editing"),
    ("@nemesis-oss/termina-genui", "Generative UI for terminal apps — renders agent-streamed declarative UI"),
    ("contractful-ts", "Contract-first HTTP and WebSocket client for TypeScript — typed methods, validation, auth, retries"),
]

# (gem name, description)
GEMS = [
    ("DhanHQ", "Ruby SDK for Dhan API v2 — ActiveModel-style models, auto-reconnecting WebSocket, order lifecycle"),
    ("ollama-client", "Deterministic, contract-driven Ruby client for the Ollama API"),
    ("contractful", "Contract-first Ruby HTTP client — closed request schemas, open responses, resilient transport"),
]


def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def npm_latest(name):
    data = fetch_json(f"https://registry.npmjs.org/{name.replace('/', '%2f')}")
    return data["dist-tags"]["latest"]


def gem_info(name):
    data = fetch_json(f"https://rubygems.org/api/v1/gems/{name}.json")
    return data["version"], int(data.get("downloads") or 0)


def kfmt(n):
    return f"{n / 1000:.1f}k+" if n >= 1000 else str(n)


def render_block(npm_rows, gem_rows):
    out = [START, ""]
    out += [
        "**npm** — [`@nemesis-oss`](https://www.npmjs.com/org/nemesis-oss) scope, plus unscoped `contractful-ts`",
        "",
        "| Package | Version | What it does |",
        "|---------|---------|---------------|",
    ]
    for name, version, desc in npm_rows:
        out.append(f"| [`{name}`](https://www.npmjs.com/package/{name}) | {version} | {desc} |")
    out += [
        "",
        "**RubyGems**",
        "",
        "| Gem | Version | Downloads | What it does |",
        "|-----|---------|-----------|--------------|",
    ]
    for name, version, downloads, desc in gem_rows:
        out.append(f"| [`{name}`](https://rubygems.org/gems/{name}) | {version} | {kfmt(downloads)} | {desc} |")
    out += ["", END]
    return "\n".join(out)


def main(write=True):
    try:
        npm_rows = [(name, npm_latest(name), desc) for name, desc in NPM]
        gem_rows = [(name, *gem_info(name), desc) for name, desc in GEMS]
    except Exception as exc:  # network or schema failure: leave README untouched
        print(f"sync aborted, README unchanged: {exc}", file=sys.stderr)
        return 1

    block = render_block(npm_rows, gem_rows)
    if not write:
        print(block)
        return 0

    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        print("packages markers missing from README.md", file=sys.stderr)
        return 1
    start = text.index(START)
    end = text.index(END) + len(END)
    new_text = text[:start] + block + text[end:]
    if new_text == text:
        print("packages table already up to date")
        return 0
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    print(f"updated packages table: {len(npm_rows)} npm packages, {len(gem_rows)} gems")
    return 0


if __name__ == "__main__":
    dry_run = "--print" in sys.argv
    sys.exit(main(write=not dry_run))
