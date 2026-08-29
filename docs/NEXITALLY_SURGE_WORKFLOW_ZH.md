# 奶昔（Nexitally）→ Surge 当前标准流程

这份文档记录当前已经实际验证过的生产流程，目的是以后即使没有 AI，也可以照着手工完成奶昔 Surge Profile 的更新。

## 一句话结论

**奶昔官方 Surge Profile 负责线路层；我们只维护策略层。**

- 奶昔负责：`[General]`、`[Proxy]`、`[Host]`，以及官方 Profile 里其他与线路相关的非空段。
- 我们负责：在 `[General]` 中补两行 IPv6、完整替换 `[Proxy Group]`、完整替换 `[Rule]`。
- Surge 负责：Smart、fallback、`SYSTEM`、`LAN`、`GEOIP,CN`，以及外部 `RULE-SET` 的缓存和更新。
- Tower 不再参与奶昔的日常生产流程。

## 为什么不用 Tower 处理奶昔

Tower 能正确解析节点，但会重新生成 Profile，因此可能丢掉奶昔原版里和线路相关的重要内容，例如：

- `block-quic`
- `hijack-dns`
- 完整的 `skip-proxy`
- `tun-excluded-routes`
- 奶昔自己的 `encrypted-dns-server`
- `use-local-host-item-for-proxy = true`
- `[Host]` 中的节点域名映射

这些内容属于机场对自己线路的适配，不应该被我们用通用模板覆盖。

## 平时正常使用的两份 Profile

### My Profile

用于自己的设备。

策略：

- 普通境外流量 → 香港 Smart
- AI → 台湾 Smart，台湾不可用时 fallback 到日本 Smart
- Crypto → 台湾节点
- Microsoft → 默认 DIRECT，可手动切香港
- Apple → 默认 DIRECT，可手动切香港
- Netflix → 默认香港，可手动选择新加坡 / 美国 / 日本
- 中国大陆 → DIRECT
- FINAL → 香港

Crypto 规则使用较干净的 v2fly `category-cryptocurrency`（通过 Geosite2Surge 转成 Surge 可用格式）。不追求第三方统计、风控、CDN 请求 100% 都命中 Crypto；只要交易所核心请求正确走台湾即可。

对应模板：

- `profiles/general-ipv6.patch.conf`
- `profiles/surge-groups-my.conf`
- `profiles/surge-rules-my.conf`

### Family Profile

给家庭设备使用，逻辑与 My Profile 基本一致，但**完全没有 Crypto 策略和 Crypto 规则**。

对应模板：

- `profiles/general-ipv6.patch.conf`
- `profiles/surge-groups-family.conf`
- `profiles/surge-rules-family.conf`

## 奶昔订阅更新时的标准步骤

### 1. 打开奶昔的临时订阅窗口

先登录奶昔，开启限时订阅。

如果当时奶昔网站需要代理才能访问，直接使用当前仍能工作的旧奶昔 Profile 打开网站即可。不要先删除旧 Profile。

### 2. 在 Surge 更新“官方奶昔 Profile”

始终保留一份**完全未经修改的官方托管 Profile**。

这份官方 Profile 用于：

- 获取最新节点；
- 获取最新 `[General]`；
- 获取最新 `[Host]`；
- 获取奶昔新增或调整的其他线路设置。

### 3. 复制一份官方 Profile

在 Surge 里复制最新官方 Profile，后续只修改复制出来的工作副本。

**官方托管 Profile 永远不改。**

### 4. 删除工作副本顶部的 `#!MANAGED-CONFIG`

工作副本必须删除：

```ini
#!MANAGED-CONFIG ...
```

否则以后 Surge 刷新奶昔订阅时，可能把我们的 `[Proxy Group]` 和 `[Rule]` 全部覆盖掉。

### 5. `[General]`：保留奶昔原版，只补 IPv6

不要拿旧的 `[General]` 覆盖新的，也不要用一个通用 `[General]` 模板整体替换。

以**最新奶昔官方 `[General]`** 为准，只确认加入：

```ini
ipv6 = true
ipv6-vif = auto
```

放在 `[General]` 内任意正常位置即可，例如 `block-quic = all` 后面。

奶昔原版中的这些配置默认全部保留：

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

除非以后有明确理由，否则不要主动改奶昔已经验证过的这些网络层参数。

### 6. `[Proxy]`：完全不动

`[Proxy]` 始终使用最新奶昔官方 Profile 的内容。

不要：

- 手工改节点地址；
- 把旧节点复制回来；
- 把节点、密码或订阅 URL 上传到 GitHub。

### 7. `[Proxy Group]`：整段替换

My Profile：用 `profiles/surge-groups-my.conf` 全部替换。

Family Profile：用 `profiles/surge-groups-family.conf` 全部替换。

不要保留奶昔原版那些把所有节点重复写进每个策略组的大型 `[Proxy Group]`。

我们的组通过 Surge 原生：

```text
smart
fallback
include-all-proxies=true
policy-regex-filter
```

动态收集香港、台湾、日本等节点。

### 8. `[Rule]`：整段替换

My Profile：用 `profiles/surge-rules-my.conf`。

Family Profile：用 `profiles/surge-rules-family.conf`。

当前规则大致顺序：

```text
Surge LAN → DIRECT
Surge SYSTEM → DIRECT

ACL4 UnBan → DIRECT
ACL4 广告规则 → REJECT
GoogleFCM → Node Select
GoogleCN / SteamCN → DIRECT

My：Crypto → 台湾
AI → 台湾 → 日本 fallback
Netflix → Netflix 组

Microsoft → Microsoft
Apple → Apple
ProxyLite → 香港

ChinaDomain → DIRECT
ChinaCompanyIp → DIRECT
GEOIP,CN → DIRECT

FINAL → 香港
```

Family 版仅删除 Crypto 那一层，其他顺序一致。

## 最重要的禁止事项：不要再远程 include 整个 Rule/Profile

不要使用这种结构：

```ini
#!include https://...
```

尤其不要让本地主 Profile 的 `[Rule]` 依赖 GitHub 上的一整个远程片段。

在中国大陆环境中，这可能形成启动死循环：Surge 还没有规则和代理能力时，就必须先访问被墙的远程 Profile，结果卡在 `Downloading Profile...`。

### 正常的外部 `RULE-SET` 没有问题

这种是正常 Surge 用法：

```ini
RULE-SET,https://...,Policy,update-interval=86400
```

区别是：

- `#!include`：把 Profile 结构本身变成远程依赖；
- `RULE-SET`：只是独立规则资源，由 Surge 单独缓存、更新。

所以当前生产方案继续使用外部 `RULE-SET`，但不再远程 include 整个 Profile 或整个 `[Rule]`。

## `[Host]` 和其他奶昔段怎么处理

`[Host]` 必须使用**最新官方奶昔 Profile** 中的内容，不要长期保存一份旧 `[Host]` 反复覆盖。

原因是奶昔启用了：

```ini
use-local-host-item-for-proxy = true
```

因此 `[Host]` 可能直接参与代理节点本身的域名解析。奶昔以后换入口域名或映射时，旧 `[Host]` 可能失效。

对于官方 Profile 中未来出现的其他非空段，例如：

```text
[Rewrite]
[Script]
[MITM]
[Host]
```

默认原则都是：**先原样保留奶昔最新版，除非我们明确知道为什么要改。**

## 更新后快速检查

重新生成 My / Family 工作副本后，至少检查：

1. Profile 可以立即正常启动，没有卡在 `Downloading Profile...`；
2. 香港 / 台湾 / 日本 Smart 组里都有正确节点；
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

这通常是奶昔 `block-quic = all` 正常生效，不代表规则错误。应用一般会回退到 HTTPS/TCP。

## Crypto 命中率原则

当前不追求 Crypto App 里每一个第三方请求都走台湾。

例如交易所可能同时调用：

- 风控服务；
- analytics；
- 归因平台；
- 公共 CDN。

这些第三方请求掉到香港通常没问题。只要交易所核心域名、API、静态资源和 Web3 主体正确走 Crypto 即可。

不要为了让 Recent Requests 看起来“全是台湾”就不断把第三方域名塞进 Crypto，这会让规则越来越脏。

## 节点测速原则

保留奶昔原版：

```ini
proxy-test-url = http://www.gstatic.com/generate_204
```

不为了让延迟数字“更真实”频繁改测速地址。

Surge Smart 会结合实际连接质量和历史表现；日常更应该看晚高峰真实使用体验，而不是单独看一个很低的 URL Test 数字。

## 没有 AI 时如何手工恢复

建议在本地记事本长期保存以下四份模板内容：

```text
profiles/general-ipv6.patch.conf
profiles/surge-groups-my.conf
profiles/surge-rules-my.conf
profiles/surge-groups-family.conf
profiles/surge-rules-family.conf
```

每次奶昔更新后：

```text
最新官方奶昔 Profile
→ 复制
→ 删除 #!MANAGED-CONFIG
→ General 只补 IPv6
→ Proxy 不动
→ Host 不动
→ 替换 Group
→ 替换 Rule
→ 保存并测试
```

注意：**不要把旧 `[General]`、旧 `[Host]` 当成长期模板。** 这两部分每次都从最新官方奶昔 Profile 继承。

## 安全边界

GitHub 里永远不要提交：

- 奶昔订阅 URL / token；
- 节点地址中的私有凭据；
- AnyTLS / SS / Trojan 等节点密码；
- 完整私人机场 Profile；
- 私有 `[Host]` 映射（如果会暴露节点信息）；
- MITM 私钥；
- Surge HTTP API 密钥。

GitHub 只保存可以公开的策略模板和操作文档。
