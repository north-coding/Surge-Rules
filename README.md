# surge-rules

Personal Surge routing rules and Tower-importable profile schemes.

## Runtime philosophy

The production profiles are intentionally small and opinionated:

```text
specific service rules
    ↓
China IPv4 / dual-stack GeoIP fallback
    ↓
FINAL → Hong Kong
```

A giant universal ruleset is not the runtime goal. The mirrored Loyalsoldier data remains useful as a reviewed upstream/reference source, but `proxy.txt` and `direct.txt` are **not loaded by the V0.2 Tower profiles**.

The key idea is:

- exceptions are explicit;
- China traffic is identified near the bottom;
- all otherwise-unmatched overseas traffic safely falls to Hong Kong.

## Production rules

### Manually curated / focused

- `rules/Crypto-Critical.list` — high-confidence exchange domains; manual-only.
- `rules/AI.list` — curated OpenAI, Claude, Gemini/DeepMind, xAI/Grok, Perplexity and Copilot coverage.
- `rules/Microsoft.list` — Teams / OneNote / Outlook / Microsoft 365 / OneDrive / SharePoint focus.
- `rules/Netflix.list` — dedicated Netflix routing.
- `rules/Apple-Direct.list` — Apple infrastructure where mainland DIRECT is normally beneficial; region-sensitive Apple media is deliberately not broadly forced DIRECT.

### Reviewed upstream mirror

From Loyalsoldier:

- `upstream/proxy.txt`
- `upstream/direct.txt`
- `upstream/cncidr.txt`

The first two are retained as reference/upstream data. `cncidr.txt` is used by the V0.2 profiles as the visible China IPv4 fallback.

## Tower profiles

Tower owns airport subscriptions, multi-airport node aggregation, country detection and final profile generation. Subscription URLs and proxy credentials remain local to Tower and are never stored in this repository.

### My Profile

Import in Tower:

```text
https://raw.githubusercontent.com/north-coding/Surge-Rules/main/profiles/tower-my.ini
```

Routing intent:

- `🔐 Crypto Critical` → manually selected concrete Taiwan node; no Hong Kong/DIRECT safety fallback.
- `🤖 AI` → Taiwan latency group by default; Japan alternative; individual TW/JP nodes remain selectable.
- `🪟 Microsoft` → DIRECT by default; Hong Kong can be selected if real-world Teams/Office performance is better.
- `🍎 Apple` → DIRECT by default for the focused Apple infrastructure list.
- `🎞️ Netflix` → Hong Kong by default, with Singapore / US / Japan alternatives.
- ordinary overseas traffic → Hong Kong.
- China IPv4 → mirrored CN CIDR DIRECT.
- IPv6 / IPv6-only China destinations → `GEOIP,CN` dual-stack safety net.

### Family Profile

Import in Tower:

```text
https://raw.githubusercontent.com/north-coding/Surge-Rules/main/profiles/tower-family.ini
```

Family intentionally omits Crypto Critical and keeps only the service choices needed for normal family use:

- AI → Taiwan by default;
- Microsoft → DIRECT by default;
- Netflix → Hong Kong by default;
- Apple infrastructure → DIRECT;
- Google / YouTube / Zoom and other unmatched overseas traffic → Hong Kong;
- China → DIRECT fallback.

## Country groups

Both Tower schemes create latency-selected country groups across all enabled airport subscriptions:

- Hong Kong
- Taiwan
- Japan
- Singapore
- United States
- Korea

They also keep an all-node manual toolbox group.

Country groups are `url-test`; `Crypto Critical` is deliberately a manual `select` over concrete Taiwan nodes so normal latency fluctuations do not change the financial-account exit IP.

## Tower export mode

For reliability, the recommended initial setting is to keep Tower's **“优先使用规则集” disabled**.

That means:

1. Tower downloads this scheme and its referenced lists when you explicitly import/refresh it;
2. Tower keeps those resources locally;
3. the generated Surge profile contains the converted rules locally;
4. normal Surge operation does not require GitHub to be reachable.

This avoids making `raw.githubusercontent.com` a runtime dependency from mainland networks.

Remote RULE-SET emission can still be enabled later if a smaller generated profile is preferred.

## IPv6

Both schemes declare:

```ini
ipv6 = true
```

Tower currently models this setting, but it does not emit Surge's advanced VIF setting. After exporting the final Surge profile, add this once under `[General]`:

```ini
ipv6-vif = auto
```

This allows Surge to take over IPv6 only when the current network actually has working IPv6.

The current V0.2 routing uses the reviewed IPv4 `cncidr.txt` plus Surge's built-in `GEOIP,CN` as a dual-stack safety net. A separately reviewed China IPv6 CIDR mirror can be added later without changing the higher-level profile architecture.

## Upstream update policy

Loyalsoldier publishes frequently. This repository does **not** automatically promote upstream changes to `main`.

The scheduled workflow:

1. downloads the selected upstream files;
2. performs sanity checks;
3. compares them with the current mirror;
4. creates or refreshes a review PR when something changed;
5. never auto-merges the PR.

`rules/Crypto-Critical.list` is never touched by upstream sync.

## Critical-rule maintenance policy

For sensitive manually curated lists:

- prefer `DOMAIN-SUFFIX` / exact `DOMAIN`;
- use a narrow `DOMAIN-KEYWORD` only when there is a clear technical reason;
- do not add generic shared CDN, CAPTCHA, analytics or payment infrastructure merely because an app touched it.

CoinSpot, Swyftx and Coinbase AU are deliberately excluded from the Taiwan-oriented Crypto Critical policy; they belong to the separate Australia profile/workflow.

## Security

Never commit:

- airport/subscription URLs or tokens;
- proxy node passwords;
- private profile credentials;
- MITM CA private material.
