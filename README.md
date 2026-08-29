# surge-rules

Personal Surge policy/rule templates. This repository contains no airport subscription URL, proxy credential, private Host mapping, MITM material or other secret.

## V0.5 final workflow

The production workflow is intentionally simple and local-first:

```text
Nexitally official Surge profile
        ↓ update while the temporary subscription window is open
keep official managed profile untouched
        ↓ duplicate locally in Surge
remove #!MANAGED-CONFIG from the working copy
        ↓
keep latest provider [General] / [Proxy] / [Host] / other provider sections
        ↓
add the two IPv6 General lines
        ↓
replace [Proxy Group] + [Rule] with this repo's templates
        ↓
local daily Surge profile
```

### Ownership boundary

- **Nexitally** owns transport/network details: the latest `[Proxy]`, `[Host]`, provider-specific `[General]` settings such as QUIC/DNS/TUN behavior, and any other non-empty provider sections.
- **This repository** owns only the stable policy layer: the IPv6 General patch, `[Proxy Group]`, and `[Rule]` templates.
- **Surge** executes Smart/fallback policy groups, SYSTEM/LAN/GeoIP, and caches/updates external `RULE-SET` resources.
- **Tower is not part of the Nexitally production path.** Parsing the provider subscription through Tower can discard provider-specific General/Host behavior. It can still be used independently for other subscriptions if useful.

## Critical bootstrap rule

Do **not** remotely include the whole `[Rule]` section or another profile from GitHub:

```ini
#!include https://...
```

The main working profile must stay local and independently loadable. A remote profile/include can create a bootstrap dependency when GitHub is inaccessible before Surge routing is active.

External rule resources are different and remain normal Surge usage:

```ini
RULE-SET,https://...,Policy,update-interval=86400
```

They are independent cached resources rather than the structure of the main profile. Their refresh can fail independently without turning the working profile itself into a remote include.

## Updating Nexitally

When the provider subscription needs a refresh:

1. open Nexitally and enable the temporary subscription window;
2. update the untouched official Nexitally Surge profile;
3. duplicate that newest official profile locally;
4. remove the duplicate's `#!MANAGED-CONFIG ...` line so a later provider refresh cannot overwrite custom policy/rules;
5. keep the newest provider `[General]`, `[Proxy]`, `[Host]` and any other provider-owned non-empty sections;
6. add the two lines from `profiles/general-ipv6.patch.conf` to `[General]`;
7. replace `[Proxy Group]` with the appropriate My or Family template;
8. replace `[Rule]` with the appropriate My or Family template;
9. validate the profile before making it daily-use.

Do not carry an old `[Host]` forward blindly. The provider may change node-host mappings, so the latest official profile is always the source of truth for provider-owned sections.

## My Profile

Use:

- `profiles/general-ipv6.patch.conf`
- `profiles/surge-groups-my.conf`
- `profiles/surge-rules-my.conf`

Policy intent:

- ordinary overseas traffic → Hong Kong Smart;
- AI → Taiwan Smart, Japan fallback;
- Crypto → concrete Taiwan proxies only;
- Microsoft → DIRECT by default, Hong Kong available manually;
- Apple → DIRECT by default, Hong Kong available manually;
- Netflix → Hong Kong by default, Singapore / US / Japan selectable;
- all country pools use native Surge `smart` with `include-all-proxies=true` and regex filtering;
- `Manual Select` contains every concrete provider proxy.

The Crypto classifier intentionally uses the cleaner v2fly `category-cryptocurrency` data converted for Surge by Geosite2Surge. It covers the core exchanges/wallet/Web3 ecosystem without trying to force every third-party analytics, fraud-detection or CDN request into the Crypto policy. A provider app may therefore have some auxiliary requests fall through to ordinary Hong Kong routing; that is intentional unless it causes a real functional problem.

## Family Profile

Use:

- `profiles/general-ipv6.patch.conf`
- `profiles/surge-groups-family.conf`
- `profiles/surge-rules-family.conf`

Family intentionally omits Crypto. It retains:

- ordinary overseas → Hong Kong Smart;
- AI → Taiwan Smart → Japan fallback;
- Microsoft / Apple → DIRECT by default;
- Netflix regional selection;
- China DIRECT and Hong Kong FINAL.

## Production rule order

My Profile:

```text
Surge LAN → DIRECT (no-resolve)
Surge SYSTEM → DIRECT

ACL4 UnBan → DIRECT
ACL4 BanAD / BanProgramAD → REJECT
ACL4 GoogleFCM → Node Select
ACL4 GoogleCN / SteamCN → DIRECT

v2fly category-cryptocurrency → Crypto / Taiwan
Nexitally Extra_AI → AI / Taiwan→Japan
ACL4 Netflix → Netflix

ACL4 Microsoft → Microsoft
ACL4 Apple → Apple
ACL4 ProxyLite → Node Select / Hong Kong
ACL4 ChinaDomain → DIRECT
ACL4 ChinaCompanyIp → DIRECT
Surge GEOIP,CN → DIRECT

FINAL → Node Select, dns-failed
```

Family is identical except the Crypto layer is omitted.

The ordering follows ACL4's mature precedence principle: local/system safety first, unblock/ad/direct exceptions early, GoogleFCM before the overlapping GoogleCN layer, service-specific policies before broad foreign routing, `ProxyLite` before China IP decisions, then China domain/company-IP/GeoIP and FINAL last.

## Upstreams

Current production templates use:

- Surge native `SYSTEM`, `LAN` and `GEOIP,CN`;
- ACL4SSR for UnBan, ad rules, GoogleFCM, GoogleCN, SteamCN, Netflix, Microsoft, Apple, ProxyLite, ChinaDomain and ChinaCompanyIp;
- Geosite2Surge / v2fly `category-cryptocurrency` for the My Profile Crypto classifier;
- Nexitally `Extra_AI` for AI classification.

The external rule URLs use `rawstatic.com`, matching the provider's deployed delivery pattern that has been verified in the current Surge profile. This is a delivery choice, not a guarantee that every network can always reach the mirror directly.

Locally maintained lists under `rules/` remain historical/reference material only. Production routing does not depend on them.

## General settings

Do not replace the provider's entire `[General]` section with a generic template. Preserve the newest Nexitally values, including settings such as:

```text
block-quic
hijack-dns
skip-proxy
dns-server
proxy-test-url
tun-excluded-routes
encrypted-dns-server
use-local-host-item-for-proxy
```

Only ensure these two lines are present:

```ini
ipv6 = true
ipv6-vif = auto
```

The provider's `[Host]` must also be retained because `use-local-host-item-for-proxy = true` may make those mappings part of node resolution.

## Offline recovery note

For manual recovery without AI, keep a local note containing the contents of:

- `general-ipv6.patch.conf`;
- `surge-groups-my.conf` and `surge-rules-my.conf`;
- `surge-groups-family.conf` and `surge-rules-family.conf`.

Do **not** treat an old saved `[Host]` or `[General]` as canonical. Copy those from the newest official provider profile each time.

## Validation

Before switching a newly rebuilt profile into daily use, check:

1. Hong Kong, Taiwan and Japan Smart groups contain the expected nodes;
2. My Profile Crypto contains concrete Taiwan nodes and exchange core requests such as Binance/Bybit/OKX can hit Taiwan;
3. AI normally uses Taiwan and can fall back to Japan;
4. Apple system traffic is DIRECT where expected;
5. ordinary overseas traffic falls to Hong Kong;
6. a normal mainland service is DIRECT;
7. the profile starts normally and is not waiting on a remote `#!include`.

QUIC requests showing `QUIC-BLOCK` are expected while the provider keeps `block-quic = all`; applications normally retry over HTTPS/TCP.

## Security

Never commit:

- airport/subscription URLs or tokens;
- proxy node host credentials or passwords;
- a full private provider profile;
- provider-specific private Host mappings if they expose subscription/node details;
- MITM CA private material;
- HTTP API keys.
