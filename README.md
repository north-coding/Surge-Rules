# surge-rules

Personal Surge routing rules with reviewed upstream sync and curated critical rules.

## Design

This repository deliberately separates two trust levels:

1. **Curated critical rules** — manually reviewed and changed only on purpose.
2. **Upstream routing data** — mirrored from mature upstream projects, updated through a reviewable pull request rather than being pushed directly into production.

The first production-critical file is:

- `rules/Crypto-Critical.list` — manually maintained exchange domains that must be routed through a stable crypto policy.

The base routing mirror is sourced from [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules):

- `upstream/proxy.txt`
- `upstream/direct.txt`
- `upstream/cncidr.txt`

## Recommended Surge rule order

```ini
[Rule]

RULE-SET,LAN,DIRECT,no-resolve

# Highest priority: explicitly reviewed sensitive services.
RULE-SET,https://raw.githubusercontent.com/north-coding/surge-rules/main/rules/Crypto-Critical.list,🔐 Crypto

# Base routing: proxy decisions before direct decisions.
RULE-SET,https://raw.githubusercontent.com/north-coding/surge-rules/main/upstream/proxy.txt,🚀 节点选择,force-remote-dns
RULE-SET,https://raw.githubusercontent.com/north-coding/surge-rules/main/upstream/direct.txt,DIRECT

# IP fallback must stay below domain/ruleset routing and immediately above FINAL.
RULE-SET,https://raw.githubusercontent.com/north-coding/surge-rules/main/upstream/cncidr.txt,DIRECT

FINAL,🚀 节点选择,dns-failed
```

`cncidr.txt` is intentionally near the bottom. This avoids placing an IP-based fallback above later domain-based rules.

## Upstream update policy

Loyalsoldier publishes very frequently. This repository does **not** automatically promote every upstream change to `main`.

The scheduled workflow:

1. downloads the three upstream files;
2. performs basic sanity checks;
3. compares them with the current mirror;
4. creates or refreshes a review branch/PR when something changed;
5. never auto-merges the PR.

This creates a stability boundary:

```text
Loyalsoldier
    ↓
scheduled check
    ↓
review PR
    ↓
manual merge
    ↓
Surge
```

## Crypto-Critical maintenance policy

`Crypto-Critical.list` is never overwritten by an upstream sync.

Rules should be added only when the domain is attributable to the target platform with high confidence.

Prefer:

```text
DOMAIN-SUFFIX,example.com
```

Avoid broad keywords unless there is a strong reason:

```text
DOMAIN-KEYWORD,example
```

Do **not** add shared infrastructure merely because it appears while an exchange app is open, for example:

- `gstatic.com`
- `recaptcha.net`
- generic Cloudflare domains
- generic analytics/CDN domains

Those may be used by unrelated apps.

## Deliberate exclusions

CoinSpot, Swyftx and region-specific Coinbase AU routing are intentionally not included in the Taiwan-oriented `Crypto-Critical.list`. They should be handled by an Australia-specific routing policy/profile.

## Manual upstream sync

```bash
python3 scripts/sync_upstream.py
```

The script downloads:

- `https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/proxy.txt`
- `https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/direct.txt`
- `https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/cncidr.txt`

## Security

Do not commit:

- airport/subscription URLs or tokens
- proxy node passwords
- private profile credentials
- MITM CA private material
