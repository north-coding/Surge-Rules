# surge-rules

Personal Surge routing rules and Tower-importable bootstrap schemes.

## V0.4 architecture

The production boundary is intentionally simple:

- **Tower** owns airport subscriptions, multi-airport aggregation and concrete `[Proxy]` entries.
- **Surge** owns policy groups, Smart selection, fallback behavior, built-in rule sets, GeoIP and production routing.
- **GitHub** stores public routing templates and references; no subscription URL, node credential or secret belongs here.

After Tower exports a profile, its generated `[Proxy Group]` and `[Rule]` sections are discarded. Surge uses the local policy-group template plus a remotely included rule section.

```text
Tower subscriptions
      ↓
concrete [Proxy] entries
      ↓
Surge include-all-proxies + regex
      ↓
Smart country pools / service groups
      ↓
Surge RULE-SET / GeoIP routing
```

## My Profile

Tower bootstrap:

```text
https://raw.githubusercontent.com/north-coding/Surge-Rules/main/profiles/tower-my.ini
```

After export:

1. keep Tower's `[Proxy]` section;
2. replace `[Proxy Group]` with `profiles/surge-groups-my.conf`;
3. replace `[Rule]` with:

```ini
[Rule]
#!include https://raw.githubusercontent.com/north-coding/Surge-Rules/main/profiles/surge-rules-my.dconf
```

4. confirm `[General]` contains:

```ini
ipv6 = true
ipv6-vif = auto
```

### Policy intent

- `Node Select` defaults to the Hong Kong Smart pool.
- `AI` is a Surge `fallback`: Taiwan Smart first, Japan Smart second.
- `Crypto` is a manual `select` over concrete Taiwan proxies only, plus `REJECT`; select one concrete Taiwan node and keep it pinned when a stable exchange exit IP matters.
- `Microsoft` defaults DIRECT with Hong Kong available manually.
- `Apple` defaults DIRECT with Hong Kong available manually.
- `Netflix` defaults Hong Kong with Singapore / US / Japan alternatives.
- country groups are native Surge `smart` groups populated with `include-all-proxies=true` and `policy-regex-filter`.
- `Manual Select` automatically contains every concrete proxy.

## Family Profile

Tower bootstrap:

```text
https://raw.githubusercontent.com/north-coding/Surge-Rules/main/profiles/tower-family.ini
```

Use `profiles/surge-groups-family.conf` for `[Proxy Group]` and remotely include `profiles/surge-rules-family.dconf` for `[Rule]`.

Family intentionally omits the Crypto policy while retaining AI Taiwan→Japan fallback, Apple/Microsoft choices, Netflix regional selection, Smart country pools, China DIRECT and Hong Kong FINAL.

## Production rule order

The My Profile uses this order:

```text
Surge LAN → DIRECT (no-resolve)
Surge SYSTEM → DIRECT

ACL4 UnBan → DIRECT
ACL4 BanAD / BanProgramAD → REJECT
ACL4 GoogleCN / SteamCN → DIRECT

v2fly category-cryptocurrency → Crypto / Taiwan
v2fly category-ai-!cn → AI fallback
ACL4 Netflix → Netflix

ACL4 Microsoft → Microsoft
ACL4 Apple → Apple
ACL4 ProxyLite → Node Select
ACL4 ChinaDomain → DIRECT
ACL4 ChinaCompanyIp → DIRECT
Surge GEOIP,CN → DIRECT

FINAL → Node Select, dns-failed
```

This intentionally follows ACL4's mature ordering principle: local/system safety first, unbreak/ad/direct exceptions early, service-specific overrides before the general foreign-proxy layer, `ProxyLite` before all China IP decisions, then China domain/company-IP/GeoIP fallbacks, and FINAL last.

Important details:

- `SYSTEM` and `LAN` are Surge-maintained internal rule sets and may improve as Surge itself updates.
- `GEOIP,CN` uses Surge's auto-updated MaxMind country database and handles both IPv4 and IPv6, so V0.4 no longer needs separate production China IPv4/IPv6 CIDR subscriptions.
- Crypto, AI, Netflix, Apple, Microsoft and ProxyLite use `extended-matching` where useful so TLS SNI / HTTP Host can still classify connections whose target is an IP literal.
- `FINAL,Node Select,dns-failed` lets the Hong Kong proxy resolve an otherwise-unmatched hostname remotely when local DNS fails during GeoIP evaluation.
- domain/service rules stay above the GeoIP fallback.
- AI stays above Microsoft so Copilot traffic follows the AI policy instead of the broader Microsoft policy.

## Maintained upstreams

V0.4 minimizes locally maintained classification rules:

- v2fly `category-cryptocurrency` via Geosite2Surge for Crypto;
- v2fly `category-ai-!cn` via Geosite2Surge for AI;
- ACL4SSR for Netflix, Apple, Microsoft, ProxyLite, GoogleCN, SteamCN, ChinaDomain, ChinaCompanyIp, UnBan and ad rules;
- Surge's own SYSTEM, LAN and auto-updated GeoIP database for platform/network baselines.

Geosite2Surge is a mechanical converter that refreshes from `v2fly/domain-list-community` on a daily workflow, allowing Surge to consume v2fly categories without us copying hundreds of domains locally.

The old local `rules/Crypto-Critical.list`, `rules/AI.list`, `rules/Netflix.list`, Apple/Microsoft focused lists and mirrored Loyalsoldier/ChinaIPv6 data may remain useful as historical/reference material, but V0.4 production routing does not depend on them.

Public classification resources can update automatically in Surge. High-risk secrets and airport subscriptions never enter GitHub.

## Installation validation

Before making a newly exported profile the daily profile, verify in Surge that:

1. the Hong Kong, Taiwan and Japan Smart groups contain the expected concrete nodes;
2. `Crypto` contains concrete Taiwan nodes and one is explicitly selected;
3. `AI` resolves through Taiwan in normal conditions and can fall back to Japan;
4. Apple system traffic such as `*.ls.apple.com` is DIRECT;
5. ordinary Google traffic uses Hong Kong while GoogleCN-only traffic remains DIRECT;
6. a normal mainland service is DIRECT and an unmatched foreign service falls to Hong Kong.

This validation matters because Surge substitutes DIRECT if a policy group ends up with no usable members; the regex-built country groups therefore must be checked once after a new node naming scheme or airport is introduced.

## Security

Never commit:

- airport/subscription URLs or tokens;
- proxy node passwords;
- private profile credentials;
- MITM CA private material;
- HTTP API keys.
