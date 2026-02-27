# WEB Invisishield Product Q&A

[（中文 Q&A）](./README_CN.md) [（English Q&A）](./README.md)

> Version: v1.0  
> Updated: 2025-12  
> Audience: Enterprise users, technical teams, partner

---

## 📋 How to Use

This Q&A covers 60+ questions buyers care most about. It is organized by scenario to help you quickly understand the core capabilities and value of WEB Invisishield.

Website: https://www.id-net.cn/

---

## Table of Contents

1. [Product Positioning & Value](#1-product-positioning--value)  
2. [Technology & Compatibility](#2-technology--compatibility)  
3. [Security Capabilities](#3-security-capabilities)  
4. [Deployment & Network](#4-deployment--network)  
5. [Implementation & Delivery](#5-implementation--delivery)  
6. [Support & Services](#6-support--services)  
7. [Industry & Compliance](#7-industry--compliance)

---

## 1. Product Positioning & Value

### ⭐ Q1.1: What is WEB Invisishield? One-line intro

**A:** WEB Invisishield is a **zero-code-change web application attack-surface reduction and secure access solution**. It makes internal web apps (OA/ERP/Finance/HR/CRM) “invisible” on the public Internet while employees access them securely via a browser—no VPN and **no app changes**.
**WEB Invisishield – Put an invisibility cloak and shield on your web apps**
*We built WEB Invisishield to let businesses focus on their core work while security teams stop firefighting.*
*Zero-change compliance, zero-change in the field, easy protection for private web apps.*

**Additional note:**  
> WEB Invisishield hides OA and other internal systems from the public Internet, yet employees can still access them anytime via browser. The whole process requires zero changes to the app and can go live in as little as one day.

---

### ⭐ Q1.2: What core pain points does it solve?

**A:** Three core pain points:

| Pain Point | Problems with traditional solutions | WEB Invisishield approach |
|------------|------------------------------------|---------------------------|
| **Exposure risk** | OA/ERP/Finance/HR/CRM directly exposed to the Internet; frequent vulnerabilities (e.g., various OA 0-days) | Attack surface reduction / non-login surface reduction, invisible to attackers |
| **Weak account security** | Weak passwords everywhere, brute force is hard to stop | Real-time weak password blocking + login protection |
| **Cost** | Traditional VPN/ZTNA needs app changes, high cost | No app changes, live in a day |

**Additional note:**  
> Fits scenarios where OA is exposed to the Internet and under attack risk, apps cannot be modified, or stronger password security is needed. It solves these at once.

---

### ⭐ Q1.3: How is it different from ZTNA?

**A:**

| Dimension | ZTNA | WEB Invisishield |
|-----------|------|------------------|
| **Users** | All employees | All employees |
| **Access scope** | All internal resources | Web apps (OA/ERP/Finance/HR/CRM/Portal) |
| **Client** | Requires installation | No install, browser only |
| **Identity** | Account/password/cert | Uses the app’s own account system |
| **User friction** | Users see ZTNA login page | **Original login page, zero friction** |
| **App changes** | Needed | **Not needed** |
| **Mobile changes** | Mobile SDK | **Not needed** |

**Additional note:**  
> Core advantage: no code change for web apps to achieve attack-surface reduction and protection without affecting user experience.

---

### 💡 Q1.4: Why the name “Invisishield”?

- **Invisible:** Apps vanish from the public Internet; attackers cannot scan app APIs. In zero-change scenarios, the attack surface converges to one point (the login) and you defend there.
- **Shield:** Dual protection—gateway blocks threats, login endpoint is hardened (weak password/brute force).
- **Metaphor:** Like giving web apps an invisibility cloak plus a shield.

---

### ⭐ Q1.5: Who is it best for?

**A:**

**Best fit:**
- Internet/tech, manufacturing, energy, pharma, retail chains (OA/ERP/Finance/HR/CRM need Internet access)
- 50–2000 seat SMBs
- Using mainstream OA (Fanwei/Seeyon/Landray, etc.) or self-built apps
- Limited IT budget, cannot modify apps

**Less suitable:**
- Pure intranet, no external access (not needed)
- Mixed L7 + L4 apps → use Tiger Shield Zero Trust Access
- Non-HTTP protocols → use Tiger Shield Zero Trust Access

---

## 2. Technology & Compatibility

### ⭐ Q2.1: How is zero-change achieved?

**A:** Via **smart plugins + gateway proxy**:

```
Working principle:
1. User visits oa.company.com (resolved to gateway)
2. User logs in; gateway forwards login traffic; user authenticates in the original system
3. Smart plugin recognizes the OA login flow and detects login success
4. Gateway only knows the user is authenticated, then auto onboards. (User is unaware)
5. Subsequent business traffic is transparently proxied
```

**Key techniques:**
- **Login flow recognition:** AI engine analyzes login page structure and auto-adapts
- **Session persistence:** Transparent cookie/token pass-through

**Additional note:**  
> Analogy: like installing a smart gate at the OA entrance. After the first successful badge swipe, the system remembers the auth state; subsequent visits need no repeat auth, giving a seamless secure experience.

---

### ⭐ Q2.2: Which OA/ERP/Finance/HR/CRM systems are supported?

**A:** *Currently none are supported; we need to write plugins for them.*

**OA systems:**

| OA Vendor | Supported Versions | Compatibility | Go-live Time |
|-----------|--------------------|---------------|--------------|
| **Fanwei OA** | v8.0–v10.0 | ✅ Prebuilt plugin | 30 min |
| **Seeyon OA** | A8+, G6+ | ✅ Prebuilt plugin | 30 min |
| **Landray EKP** | V13–V16 | ✅ Prebuilt plugin | 30 min |
| **Tongda OA** | 2017+ | ✅ Prebuilt plugin | 30 min |
| **Other OA** | - | ⚠️ Custom | 1 day |

**ERP systems:**

| ERP Vendor | Supported Versions | Compatibility | Go-live Time |
|------------|--------------------|---------------|--------------|
| **Yonyou NC** | NC6.x | ✅ Prebuilt | 30 min |
| **Yonyou U8** | U8+ | ✅ Prebuilt | 30 min |
| **Kingdee K/3** | K/3 WISE | ✅ Prebuilt | 30 min |
| **Kingdee EAS** | 7.x–8.x | ✅ Prebuilt | 30 min |
| **Other ERP** | - | ⚠️ Custom | 1 day |

**Finance systems:**

| Finance Software | Supported Versions | Compatibility | Go-live Time |
|------------------|--------------------|---------------|--------------|
| **Yonyou Changjie** | T+/T6 | ✅ Prebuilt | 30 min |
| **Kingdee KIS** | Pro/Flagship | ✅ Prebuilt | 30 min |
| **Inspur Finance** | Mainstream versions | ✅ Prebuilt | 30 min |
| **Other finance** | - | ⚠️ Custom | 1 day |

**HR systems:**

| HR System | Supported Versions | Compatibility | Go-live Time |
|-----------|--------------------|---------------|--------------|
| **Beisen** | Mainstream | ✅ Prebuilt | 30 min |
| **Yonyou HR** | NC-HR/U8-HR | ✅ Prebuilt | 30 min |
| **Kingdee HR** | K3-HR/EAS-HR | ✅ Prebuilt | 30 min |
| **Custom HR** | - | ⚠️ Custom | 1 day |

**CRM systems:**

| CRM System | Supported Versions | Compatibility | Go-live Time |
|------------|--------------------|---------------|--------------|
| **Yonyou CRM** | U9/NC-CRM | ✅ Prebuilt | 30 min |
| **Kingdee CRM** | K3-CRM | ✅ Prebuilt | 30 min |
| **Fxiaoke** | Mainstream | ✅ Prebuilt | 30 min |
| **Xiaoshouyi** | Mainstream | ✅ Prebuilt | 30 min |
| **Other custom CRM** | - | ⚠️ Custom | 1 day |

**Other custom systems:**
- MES, BI, ticketing, etc.: ⚠️ Custom, ~1 day to go live

**Extra notes:**
- ✅ Prebuilt: out of the box, just select the plugin
- ⚠️ Custom: vendor can assist; usually 1–2 days

---

### Q2.3: If we use a niche or custom app, can you support it?

**A:** Yes, if the following hold; follow the plugin guide or request vendor plugin service.

**Must have:**
- ✅ HTTP/HTTPS-based
- ✅ Web login page (form submit or API call)
- ✅ Session cookie or token after login

**Supported with customization:**
- ⚠️ Multi-step login (e.g., phone verify then password)
- ⚠️ Complex CAPTCHA (OCR integration)
- ⚠️ Dynamic token (CSRF protection)

**Not supported:**
- ❌ Pure desktop client (C/S, non-B/S)

**Additional note:**  
> 99% of HTTP/HTTPS web apps can be supported. Provide a test account; engineering can verify remotely, typically giving a feasibility verdict within 2 hours. This check is free.

---

### Q2.4: Does mobile (phone/iPad) work?

**A:** Fully supported, with better experience:

**Supported:**
- ✅ Mobile browsers
- ✅ H5 inside WeCom/DingTalk/Feishu
- ✅ WeChat mini program (e.g., OA mini program)
- ✅ iPad tablet access

**Mobile advantages:**
- No app or VPN client to install

---

### Q2.5: Bandwidth requirements? Will it slow access?

**A:**

**Bandwidth:**
- Cloud gateway: no special requirement, carrier backbone (BGP multi-line)
- Private gateway: recommend uplink ≥10 Mbps (for ~200 users)

**Latency impact:**
| Scenario | Added latency | Note |
|----------|---------------|------|
| Cloud GW (same city) | +10–30 ms | Barely noticeable |
| Cloud GW (cross-province) | +30–80 ms | Slight |
| Private GW (local) | +5–10 ms | Negligible |

**Optimizations:**
- Static asset caching (JS/CSS/images)
- Gzip compression (50%+ traffic cut)
- Connection pooling (fewer handshakes)

**Measured data:**  
> Manufacturing customer (300 users), Fanwei OA: login time from 3.2s down to 1.8s (cache benefit); business ops unchanged.

---

### Q2.6: Will it conflict with existing firewall/WAF?

**A:** No; they are complementary:

**Network topology:**
```
User → WAF → Gateway (WEB Invisishield) → Internal FW → Backend app
```

**Roles:**
- WAF: Web attack protection (SQLi, XSS, etc.)
- WEB Invisishield: Attack-surface reduction, identity, login hardening
- Internal FW: Network-layer ACL

**Config tip:**
- FW ACL: allow only gateway IP to reach backend (further reduction)

---

### Q2.7: What’s the difference between WAF and WEB Invisishield?

**A:** They complement each other and address different layers:

| Dimension | WAF | WEB Invisishield |
|-----------|-----|------------------|
| **Core role** | Detect/block known attacks | Attack-surface reduction & identity |
| **Defense mode** | Passive: analyze traffic signatures | Active: hide the app, attacker finds no target |
| **Target** | Known vulns (SQLi, XSS, etc.) | Login security (brute force, weak passwords), non-login surface reduction |
| **Exposure** | ❌ Does not solve exposure | ✅ Core capability |
| **App changes** | Not needed | **Not needed** |
| **0-day** | Cannot defend | **Can** |
| **Bypass games** | Signature-based, cat-and-mouse | **Surface reduction, little bypass space** |

**Capability comparison:**

| Capability | WAF | WEB Invisishield | Note |
|------------|-----|------------------|------|
| Attack-surface reduction | ❌ | ✅ **Strong** | Unique to Invisishield |
| Brute-force login | ⚠️ Basic rate limit | ✅ **Strong** | Core |
| Weak password blocking | ❌ | ✅ **Unique** | Core |
| SQLi protection | ✅ Strong | ⚠️ Medium | WAF specialty |
| XSS protection | ✅ Strong | ⚠️ Medium | WAF specialty |

**Best-practice combo:**
```
Recommended:
User → WAF (known attacks) → WEB Invisishield (surface reduction + auth) → App

Effects:
- WAF: blocks SQLi, XSS, etc.
- Invisishield: invisibility + login hardening + weak password治理
- Dual-layer, complementary
```

**Budget-limited choice:**

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| OA/ERP/Finance/HR/CRM exposed to Internet | **Prioritize WEB Invisishield** | Remove exposure; attacker can’t find target |
| App already hidden, complex biz | **Consider WAF** | Business-logic vuln defense |
| Budget sufficient | **WAF + WEB Invisishield** | Best practice |

**Additional note:**  
> WAF inspects traffic for attack patterns; WEB Invisishield hides the app so attackers can’t find it. Best is both for defense-in-depth. With tight budgets, for high-risk OA start with Invisishield.

**Common questions:**

**Q: We already have WAF; still need WEB Invisishield?**  
**A:** Yes, recommended. WAF handles known attacks but not exposure. With an OA 0-day, WAF rules may lag; attackers may still break in. Invisishield makes the app invisible and stops attacks at the source. Together they’re stronger.

**Q: Can WEB Invisishield replace WAF?**  
**A:** Not fully, but it covers most core scenarios. Invisishield focuses on surface reduction, login security, and unauthorized access blocking; it has basic SQLi/XSS protection but WAF is more specialized there. Choose based on needs and budget.

---

## 3. Security Capabilities

### ⭐ Q3.1: How is attack-surface reduction achieved? Can attackers really not scan it?

**A:** Via **reverse proxy + covert forwarding**:

**Traditional (exposed):**
```
Internet → oa.company.com (public IP 1.2.3.4) → OA server

Attacker scan:
nmap 1.2.3.4 → finds 8080 open → fingerprints Fanwei OA → exploits
```

**WEB Invisishield (hidden):**
```
Internet → oa.company.com (resolves to gateway) → gateway verifies identity → internal 10.0.1.100:8080

Attacker scan:
nmap oa.company.com → only sees 443 (gateway) → cannot fingerprint backend → nowhere to attack
```

**Key techniques:**
1. **DNS:** App domain points to gateway, not real app IP
2. **Gateway identity check:** Without identity, request rejected
3. **Fingerprint hiding:** Gateway masks response headers to avoid app type/version leakage
4. **Login hardening:** Protects login from brute force/weak passwords

**Measured effect:**  
> Customer with Fanwei OA: thousands of daily scans before; after onboarding, attacks dropped to zero (no surface to find).

---

### Q3.2: How is weak password detection done?

**A:**

**When:** During user login  
**How:**  
1. Hash compare: password MD5 matched against weak password DB (1M+ common weak passwords)  
2. Rule check: length, complexity (upper/lower/digit/special)  
3. Personal info check: disallow name/employee ID/birthday as password  

**Additional note:**  
> Similar to airport scanning luggage for hazards without viewing contents; system only checks strength and doesn’t store plaintext passwords, protecting user privacy.

---

### Q3.3: How is brute-force protection implemented?

**A:**

**Policy:**
```yaml
Trigger: Same IP/user 5 failed logins within 5 minutes
Action:
  - Block IP for 5 minutes
  - Trigger alert
```

**Compared with traditional:**
| Solution | Where | Limitation | Invisishield advantage |
|----------|-------|------------|------------------------|
| Built-in app | OA itself | Rigid rules, hard to unify | Gateway unified policy, extra layer |
| WAF | Perimeter | Only known attack signatures | Surface reduction + weak password治理 |
| Firewall | Network layer | Can’t see business layer | HTTP-deep, precise block |

---

### Q3.4: Does zero-change support MFA?

**A:** v1.2 supports below MFA:

| MFA | Note | Version |
|-----|------|---------|
| **OTP token** | Google Authenticator etc. | v1.0 |

**Recommended (v1.2):**
- Regular staff: account/password login
- MFA optional bind; currently OTP supported

---

## 4. Deployment & Network

### ⭐ Q4.1: Cloud gateway vs. private gateway?

**A:**

| Dimension | Cloud Gateway (recommended) | Private Gateway |
|-----------|-----------------------------|-----------------|
| **Deployment** | Turnkey | Customer deploys (VM/container) |
| **Scenarios** | Fast go-live, small orgs | Sensitive data, compliance, large orgs |
| **Ops** | Vendor-operated, auto-upgrade | Customer-operated |
| **Latency** | Depends on node distance | Local, minimal latency |
| **HA** | Default multi-node redundancy | Customer builds HA |
| **Compliance** | Data passes vendor gateway | Data stays on-prem |

**Choice tips:**
- **Prefer cloud:** <200 users, tight budget, need fast go-live
- **Choose private:** Need dedicated gateway, highly sensitive data (finance/defense), strict compliance, large scale (1000+)

**Additional note:**  
> ~80% choose cloud for 1-day go-live. If data compliance demands on-prem, private is supported too.

---

### Q4.2: Is private gateway deployment complex? What’s needed?

**A:**

**Minimum spec:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 100 GB
- Network: Dual NIC (LAN+WAN) or single routable NIC
- OS: Ubuntu 18.04+ / Docker / K8s

**Deployment:**
1. Software installation; see “Private Gateway Deployment Guide”

**Tech support:**
- Detailed docs
- Remote assist for Professional/Annual plans

---

### Q4.3: What if a single gateway fails? HA options?

**A:**

**Cloud gateway (built-in HA):**
- Multi-node redundancy (≥2 per region)
- Auto failover (SLB load balancer)
- SLA: 99.9% availability (Pro/Annual)

**Private gateway (needs setup):**
- **Load-balancing mode:** multiple gateways + LB (Nginx/F5/Cloud LB)

**Emergency:**
- Keep a backup access path (temp revert to old login)
- 24×7 emergency response (Pro/Annual)

---

### Q4.4: What changes on the app server?

**A:** Only **network reachability** tweaks, no app changes:

**Must:**
1. **DNS:** Point access domain (e.g., oa.company.com) to gateway (CNAME)

**Optional hardening:**
1. **ACL:** Firewall only allows gateway IP to access app (further reduction)
2. **Close public exposure:** If OA had public IP, close it

**Not needed:**
- ❌ No agent
- ❌ No app code changes
- ❌ No DB changes
- ❌ No existing FW rule removals (only add)

---

## 5. Implementation & Delivery

### ⭐ Q5.1: How long from purchase to go-live?

**A:**

**Standard flow:**
| Phase | Duration | Key action |
|-------|----------|------------|
| Account setup | Instant | Auto admin access |
| Config/impl | Half day | Configure app, plugin build/test |
| Test/verify | Half day | IT host testing, fix issues |
| Pilot | 1 day | Small rollout, collect feedback |
| Full go-live | 1 day | Company-wide cutover |

**Total: ~3 working days**

---

### Q5.2: Will implementation impact current business?

**A:** **Host testing doesn’t; DNS cutover is the impact point; rollback via DNS anytime.**

**Characteristics:**
- ✅ Parallel deploy: gateway independent from existing system
- ✅ Host testing: change host file for testing, no prod impact
- ✅ Gradual: DNS cutover in stages; small pilot before full

**Risk control:**
1. **Test first:** Use test environment if available
2. **Off-peak cutover:** Change DNS in low-traffic window (e.g., 10pm)
3. **Fallback:** If issues, DNS rollback within 5 minutes

**Customer case:**  
> Manufacturing, 600-user Fanwei OA. Config Friday night, full cutover Monday morning. Zero weekend impact; minor user adaptation Monday, solved after short training.

---

## 6. Support & Services

### ⭐ Q6.1: How fast is support response?

**A:** Tiered by plan:

| Plan | Response | Channel | Hours |
|------|----------|---------|-------|
| **Trial** | 48h | Online | Workdays 9:00–18:00 |
| **Standard** | 4h | Online | Workdays 9:00–21:00 |
| **Professional** | 1h | Phone+Online | 7×12 |
| **Annual** | 30min | Dedicated group+Phone+Online | 7×24 |

**P0 emergency:**
- Definition: Core business down, widespread login failure
- Response: Pro/Annual 15 min; engineers can remote in if needed

**Additional note:**  
> Pro promises 1h, average ~15 min. Annual gets dedicated support group, typically <5 min.

---

### Q6.2: Is onsite service available?

**A:**

**Standard (remote):**
- All plans default remote (Zoom/Tencent Meeting/TeamViewer)
- 90% issues resolved remotely

**Onsite (optional purchase):**
- For: very large deployments (1000+), complex networks, explicit request
- Price: 1500 RMB/person/day (travel extra)
- Staff: Vendor-certified service center
- Includes: site survey, design, implementation, training

---

### Q6.3: Will the product keep updating? Any upgrade fee?

**A:**

**Frequency:**
- Minor (bugfix): monthly 1–2
- Major (new features): quarterly 1
- Security patches: emergency as needed

**Upgrade:**
- Cloud GW: auto, no user impact (overnight)
- Private GW: upgrade package + guide

**Cost:**
- ✅ Free during contract
- ✅ Includes new features, security patches, plugin updates
- ✅ Includes major version jump (v1.x → v2.x)

**Examples:**
- 2024 Q4: added “Weak Password Governance Report” — free to paid users
- 2024 Q3: added Feishu IdP support — free for all editions

---

### Q6.4: If we don’t renew, can we export data?

**A:** Yes, with **data migration support**:

**Exportable:**
- ✅ Access logs
- ✅ Basic configuration

**Migration help:**
- Provide APIs to migrate elsewhere
- Notify 30 days before expiry for ample time

**Additional note:**  
> We don’t lock in your data. After expiry, configs and logs can be exported to switch plans or revert architecture.

---

## 7. Industry & Compliance

### Q7.1: Does it meet MLPS 2.0 (China) requirements?

**A:** Yes, it can help you pass MLPS assessments:

| Control | MLPS requirement | Invisishield implementation |
|---------|------------------|-----------------------------|
| **Identity** | Multi-factor | Supports OTP MFA |
| **Access control** | Least privilege | No access before auth; page-level control |
| **Audit** | Logs ≥6 months | Supported (Annual can keep 6 months or extra purchase) |
| **Intrusion prevention** | Anti brute-force | Brute-force protection, login lockout |
| **Data secrecy** | Encrypted transport | Enforce HTTPS (TLS 1.2+) |

**Assessment materials:**
- Security whitepaper
- MLPS control mapping
- Assistance configuring assessment-ready policies


---

**Document version:** v1.0  
**Last updated:** Dec 2025  


