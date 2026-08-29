# 奶昔（Nexitally）→ Surge 当前标准流程

这份文档记录当前已经实际验证过的生产流程。目标是：**以后即使没有 AI，也可以只靠这一个文档完成 My Profile 和 Family Profile 的更新与恢复。**

## 一句话结论

**奶昔官方 Surge Profile 负责线路层；我们只维护策略层。**

- 奶昔负责：最新 `[General]`、`[Proxy]`、`[Host]`，以及官方 Profile 里其他与线路相关的非空段。
- 我们负责：在 `[General]` 中补两行 IPv6、完整替换 `[Proxy Group]`、完整替换 `[Rule]`。
- Surge 负责：Smart、fallback、`SYSTEM`、`LAN`、`GEOIP,CN`，以及外部 `RULE-SET` 的缓存和更新。
- Tower 不再参与奶昔的日常生产流程。

## 为什么不用 Tower 处理奶昔

Tower 能解析节点，但会重新生成 Profile，因此可能丢掉奶昔原版的线路层设置，例如：

- `block-quic`
- `hijack-dns`
- 完整 `skip-proxy`
- `tun-excluded-routes`
- 奶昔自己的 `encrypted-dns-server`
- `use-local-host-item-for-proxy = true`
- `[Host]` 中的节点域名映射

这些内容属于机场对自己线路的适配，不应由通用模板覆盖。

## 每次更新奶昔时的标准步骤

1. 登录奶昔，开启限时订阅窗口。
2. 在 Surge 更新那份**未经修改的官方奶昔托管 Profile**。
3. 复制最新官方 Profile；官方原版继续保留不动。
4. 删除工作副本顶部的 `#!MANAGED-CONFIG ...`。
5. `[General]` 以最新奶昔官方内容为准，只补 IPv6 两行。
6. `[Proxy]` 完全不动。
7. `[Host]` 完全使用最新奶昔官方内容，不拿旧版本覆盖。
8. `[Proxy Group]` 整段替换成下面的 My 或 Family 模板。
9. `[Rule]` 整段替换成下面的 My 或 Family 模板。
10. 奶昔以后若出现新的非空 `[Rewrite]`、`[Script]`、`[MITM]` 等段，默认先原样保留。
11. 保存并做快速验证。

如果当时奶昔网站本身需要代理才能登录，就用当前仍能工作的旧奶昔 Profile 打开网站。**不要先删除旧 Profile。**

---

# 一、General：只补这两行 IPv6

不要整体替换奶昔 `[General]`。在最新官方 `[General]` 中加入：

```ini
ipv6 = true
ipv6-vif = auto
```

放在 `[General]` 内正常位置即可，例如 `block-quic = all` 后面。

奶昔原版这些内容默认全部保留：

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

当前正式模板文件：`profiles/general-ipv6.patch.conf`。

---

# 二、My Profile 完整 `[Proxy Group]`

把奶昔工作副本原来的 `[Proxy Group]` **整段删除并替换为下面全文**：

```ini
[Proxy Group]

Node Select = select, 🇭🇰 Hong Kong, 🏳️‍🌈 Taiwan, 🇯🇵 Japan, 🇸🇬 Singapore, 🇺🇸 United States, 🇰🇷 Korea, Manual Select

AI = fallback, 🏳️‍🌈 Taiwan, 🇯🇵 Japan, evaluate-before-use=true, no-alert=true

Crypto = select, include-all-proxies=true, policy-regex-filter="(?i)(台湾|台灣|taiwan|taipei|台北|🇹🇼|🏳️‍🌈|\bTW\b|\bTPE\b)"

Microsoft = select, DIRECT, 🇭🇰 Hong Kong, Manual Select
Apple = select, DIRECT, 🇭🇰 Hong Kong, Manual Select
Netflix = select, 🇭🇰 Hong Kong, 🇸🇬 Singapore, 🇺🇸 United States, 🇯🇵 Japan, Manual Select

🇭🇰 Hong Kong = smart, include-all-proxies=true, policy-regex-filter="(?i)(香港|hong[ _-]*kong|🇭🇰|\bHK\b|\bHKG\b)"
🏳️‍🌈 Taiwan = smart, include-all-proxies=true, policy-regex-filter="(?i)(台湾|台灣|taiwan|taipei|台北|🇹🇼|🏳️‍🌈|\bTW\b|\bTPE\b)"
🇯🇵 Japan = smart, include-all-proxies=true, policy-regex-filter="(?i)(日本|japan|tokyo|东京|東京|osaka|大阪|🇯🇵|\bJP\b)"
🇸🇬 Singapore = smart, include-all-proxies=true, policy-regex-filter="(?i)(新加坡|狮城|獅城|singapore|🇸🇬|\bSG\b)"
🇺🇸 United States = smart, include-all-proxies=true, policy-regex-filter="(?i)(美国|美國|united[ _-]*states|america|los[ _-]*angeles|san[ _-]*jose|seattle|🇺🇸|\bUS\b|\bUSA\b)"
🇰🇷 Korea = smart, include-all-proxies=true, policy-regex-filter="(?i)(韩国|韓國|korea|seoul|首尔|首爾|🇰🇷|\bKR\b)"

Manual Select = select, include-all-proxies=true
```

My Profile 路由意图：

```text
普通境外 → 香港 Smart
AI       → 台湾 Smart → 日本 fallback
Crypto   → 台湾具体节点
Microsoft→ DIRECT
Apple    → DIRECT
Netflix  → 香港默认，可手动选择新加坡 / 美国 / 日本
中国大陆 → DIRECT
FINAL    → 香港
```

当前正式模板文件：`profiles/surge-groups-my.conf`。

---

# 三、My Profile 完整 `[Rule]`

把工作副本原来的 `[Rule]` **整段删除并替换为下面全文**：

```ini
[Rule]

# Surge native
RULE-SET,LAN,DIRECT,no-resolve
RULE-SET,SYSTEM,DIRECT

# ACL4 baseline
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/UnBan.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/BanAD.list,REJECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/BanProgramAD.list,REJECT,update-interval=86400

# Google mainland / push
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/GoogleFCM.list,Node Select,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/GoogleCN.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/SteamCN.list,DIRECT,update-interval=86400

# Special services
RULE-SET,https://rawstatic.com/ImpXada/Geosite2Surge/refs/heads/main/data/category-cryptocurrency,Crypto,update-interval=86400
RULE-SET,https://rawstatic.com/nexitallyy/ProxyRules/main/Extra_AI.list,AI,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Netflix.list,Netflix,update-interval=86400

# Microsoft / Apple
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Microsoft.list,Microsoft,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Apple.list,Apple,update-interval=86400

# Ordinary overseas override before China IP decisions
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ProxyLite.list,Node Select,update-interval=86400

# Mainland China
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ChinaDomain.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ChinaCompanyIp.list,DIRECT,update-interval=86400
GEOIP,CN,DIRECT

FINAL,Node Select,dns-failed
```

规则顺序：

```text
LAN / SYSTEM
→ ACL4 UnBan / Ads
→ GoogleFCM / GoogleCN / SteamCN
→ Crypto
→ AI
→ Netflix
→ Microsoft
→ Apple
→ ProxyLite
→ ChinaDomain
→ ChinaCompanyIp
→ GEOIP,CN
→ FINAL
```

Crypto 使用较干净的 v2fly `category-cryptocurrency`（经 Geosite2Surge 转换）。不追求交易所 App 的第三方 analytics、风控或公共 CDN 100% 都命中 Crypto；核心交易所请求正确走台湾即可。

当前正式模板文件：`profiles/surge-rules-my.conf`。

---

# 四、Family Profile 完整 `[Proxy Group]`

Family 与 My 的主要区别：**完全没有 Crypto Group。**

把 Family 工作副本原来的 `[Proxy Group]` 整段替换为：

```ini
[Proxy Group]

Node Select = select, 🇭🇰 Hong Kong, 🏳️‍🌈 Taiwan, 🇯🇵 Japan, 🇸🇬 Singapore, 🇺🇸 United States, 🇰🇷 Korea, Manual Select

AI = fallback, 🏳️‍🌈 Taiwan, 🇯🇵 Japan, evaluate-before-use=true, no-alert=true

Microsoft = select, DIRECT, 🇭🇰 Hong Kong, Manual Select
Apple = select, DIRECT, 🇭🇰 Hong Kong, Manual Select
Netflix = select, 🇭🇰 Hong Kong, 🇸🇬 Singapore, 🇺🇸 United States, 🇯🇵 Japan, Manual Select

🇭🇰 Hong Kong = smart, include-all-proxies=true, policy-regex-filter="(?i)(香港|hong[ _-]*kong|🇭🇰|\bHK\b|\bHKG\b)"
🏳️‍🌈 Taiwan = smart, include-all-proxies=true, policy-regex-filter="(?i)(台湾|台灣|taiwan|taipei|台北|🇹🇼|🏳️‍🌈|\bTW\b|\bTPE\b)"
🇯🇵 Japan = smart, include-all-proxies=true, policy-regex-filter="(?i)(日本|japan|tokyo|东京|東京|osaka|大阪|🇯🇵|\bJP\b)"
🇸🇬 Singapore = smart, include-all-proxies=true, policy-regex-filter="(?i)(新加坡|狮城|獅城|singapore|🇸🇬|\bSG\b)"
🇺🇸 United States = smart, include-all-proxies=true, policy-regex-filter="(?i)(美国|美國|united[ _-]*states|america|los[ _-]*angeles|san[ _-]*jose|seattle|🇺🇸|\bUS\b|\bUSA\b)"
🇰🇷 Korea = smart, include-all-proxies=true, policy-regex-filter="(?i)(韩国|韓國|korea|seoul|首尔|首爾|🇰🇷|\bKR\b)"

Manual Select = select, include-all-proxies=true
```

当前正式模板文件：`profiles/surge-groups-family.conf`。

---

# 五、Family Profile 完整 `[Rule]`

Family 与 My 的主要区别：**完全没有 Crypto Rule。**

把 Family 工作副本原来的 `[Rule]` 整段替换为：

```ini
[Rule]

# Surge native
RULE-SET,LAN,DIRECT,no-resolve
RULE-SET,SYSTEM,DIRECT

# ACL4 baseline
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/UnBan.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/BanAD.list,REJECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/BanProgramAD.list,REJECT,update-interval=86400

# Google mainland / push
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/GoogleFCM.list,Node Select,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/GoogleCN.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/SteamCN.list,DIRECT,update-interval=86400

# AI / Netflix
RULE-SET,https://rawstatic.com/nexitallyy/ProxyRules/main/Extra_AI.list,AI,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Netflix.list,Netflix,update-interval=86400

# Microsoft / Apple
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Microsoft.list,Microsoft,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/Apple.list,Apple,update-interval=86400

# Ordinary overseas override before China IP decisions
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ProxyLite.list,Node Select,update-interval=86400

# Mainland China
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ChinaDomain.list,DIRECT,update-interval=86400
RULE-SET,https://rawstatic.com/ACL4SSR/ACL4SSR/master/Clash/ChinaCompanyIp.list,DIRECT,update-interval=86400
GEOIP,CN,DIRECT

FINAL,Node Select,dns-failed
```

当前正式模板文件：`profiles/surge-rules-family.conf`。

---

# 六、哪些部分必须保留奶昔最新版

## `[Proxy]`

完全不动。始终使用最新官方 Profile 节点。

不要：

- 手工改节点地址；
- 把旧节点复制回来；
- 把节点、密码或订阅 URL 上传 GitHub。

## `[Host]`

必须使用**最新官方奶昔 Profile** 的内容。

因为奶昔启用了：

```ini
use-local-host-item-for-proxy = true
```

因此 `[Host]` 可能直接参与代理节点自身的域名解析。奶昔以后换入口域名或映射时，旧 `[Host]` 可能失效。

## 其他非空段

如果官方 Profile 后续出现：

```text
[Rewrite]
[Script]
[MITM]
[Host]
```

默认原则：**先原样保留最新版，除非明确知道为什么要改。**

---

# 七、最重要的禁止事项：不要远程 include 整个 Rule/Profile

不要使用：

```ini
#!include https://...
```

去远程加载整个 `[Rule]` 或整个 Profile。

在中国大陆环境中可能形成启动死循环：Surge 还没有建立规则和代理能力时，就必须先访问被墙的远程 Profile，最终卡在：

```text
Downloading Profile...
```

正常的外部 `RULE-SET` 没问题：

```ini
RULE-SET,https://...,Policy,update-interval=86400
```

区别：

- `#!include`：Profile 结构本身成为远程依赖；
- `RULE-SET`：独立规则资源，由 Surge 单独缓存和更新。

---

# 八、更新后快速检查

至少检查：

1. Profile 可以立即正常启动，没有卡 `Downloading Profile...`；
2. 香港 / 台湾 / 日本 Smart 组都有正确节点；
3. 普通境外网站走香港；
4. 中国大陆服务走 DIRECT；
5. AI 正常走台湾，台湾不可用时可 fallback 日本；
6. My Profile 中 Binance / Bybit / OKX 等核心请求能走台湾；
7. Apple / Microsoft 默认 DIRECT；
8. `FINAL,Node Select,dns-failed` 拼写正确。

如果 Recent Requests 中看到：

```text
QUIC-BLOCK
```

通常是奶昔 `block-quic = all` 正常生效，不代表规则错误。应用一般会回退到 HTTPS/TCP。

---

# 九、Crypto 命中率原则

当前不追求 Crypto App 中每一个第三方请求都走台湾。

交易所可能同时调用：

- 风控服务；
- analytics；
- 归因平台；
- 公共 CDN。

这些第三方请求掉到香港通常没问题。只要交易所核心域名、API、主要静态资源和 Web3 主体正确走 Crypto 即可。

不要为了让 Recent Requests 看起来“全是台湾”就不断把第三方域名塞进 Crypto，否则规则会越来越脏。

---

# 十、节点测速原则

保留奶昔原版：

```ini
proxy-test-url = http://www.gstatic.com/generate_204
```

不为了让延迟数字“更真实”频繁改测速地址。

Surge Smart 会结合实际连接质量和历史表现；日常更应该看晚高峰真实使用体验，而不是单独看 URL Test 数字。

---

# 十一、没有 AI 时的最短恢复流程

这份中文文档本身已经包含全部可复制模板，因此只需要拿到**最新官方奶昔 Profile**：

```text
最新官方奶昔 Profile
→ 复制一份
→ 删除 #!MANAGED-CONFIG
→ General 只补：
   ipv6 = true
   ipv6-vif = auto
→ Proxy 完全不动
→ Host 完全不动
→ My 或 Family 的 Proxy Group 全文替换
→ My 或 Family 的 Rule 全文替换
→ 其他奶昔非空段保留
→ 保存并测试
```

不要把旧 `[General]`、旧 `[Host]` 当成长期模板；这两部分每次都从最新官方 Profile 继承。

---

# 十二、安全边界

GitHub 永远不要提交：

- 奶昔订阅 URL / token；
- 节点地址中的私有凭据；
- AnyTLS / SS / Trojan 等节点密码；
- 完整私人机场 Profile；
- 私有 `[Host]` 映射（如果会暴露节点信息）；
- MITM 私钥；
- Surge HTTP API 密钥。

GitHub 只保存可以公开的策略模板和操作文档。
