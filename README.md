# surge-rules

Personal Surge routing rules and Tower-importable bootstrap schemes.

## V0.4 architecture

The production boundary is intentionally simple:

- **Tower** owns airport subscriptions, multi-airport aggregation and concrete `[Proxy]` entries.
- **Surge** owns policy groups, Smart selection, fallback behavior, built-in rule sets and production routing.
- **GitHub** stores public routing templates and owner-maintained service rules; no subscription URL, node credential or secret belongs here.

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
Surge RULE-SET routing
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
Surge SYSTEM → DIRECT
Surge LAN → DIRECT (no-resolve)

v2fly category-cryptocurrency → Crypto / Taiwan
AI → AI fallback
Netflix → Netflix

ACL4 UnBan / ad rules / GoogleCN / SteamCN
ACL4 Microsoft → Microsoft
ACL4 Apple → Apple
ACL4 ProxyLite → Node Select
ACL4 ChinaDomain → DIRECT
ACL4 ChinaCompanyIp → DIRECT

China IPv4 fallback → DIRECT
China IPv6 fallback → DIRECT
FINAL → Node Select, dns-failed
```

Important details:

- `SYSTEM` and `LAN` are Surge-maintained internal rule sets and may improve as Surge itself updates.
- Crypto, AI, Netflix, Apple, Microsoft and ProxyLite use `extended-matching` where useful so TLS SNI / HTTP Host can still classify connections whose target is an IP literal.
- `FINAL,Node Select,dns-failed` lets the Hong Kong proxy resolve an otherwise-unmatched hostname remotely when local DNS fails during IP-rule evaluation.
- domain/service rules stay above China IP fallbacks.

## Crypto source

The production Crypto rule is not the old manual `rules/Crypto-Critical.list`.

It directly references `category-cryptocurrency` from `ImpXada/Geosite2Surge`, which converts the upstream `v2fly/domain-list-community` geosite data into Surge syntax on a daily workflow. This gives broad CEX / wallet / DeFi coverage without maintaining hundreds of domains locally.

`rules/Crypto-Critical.list` remains in the repository only as a historical/reference list and is not loaded by V0.4 production routing.

## Public upstreams

V0.4 directly follows mature upstream classification where appropriate:

- v2fly `category-cryptocurrency` via Geosite2Surge;
- ACL4SSR for Apple, Microsoft, ProxyLite, GoogleCN, ChinaDomain, ChinaCompanyIp and selected direct/ad lists;
- reviewed China IPv4 mirror in `upstream/cncidr.txt`;
- commit-pinned China IPv6 rules from Centralmatrix3/Matrix-io.

Public low-risk classification can update automatically in Surge. High-risk secrets and airport subscriptions never enter GitHub.

## Security

Never commit:

- airport/subscription URLs or tokens;
- proxy node passwords;
- private profile credentials;
- MITM CA private material;
- HTTP API keys.
