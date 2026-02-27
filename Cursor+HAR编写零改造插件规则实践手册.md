# Cursor+HAR 编写零改造插件规则实践手册

目标：让团队按固定步骤，用 HAR 抓包 + 零改造文档 + Cursor，快速产出可校验的插件配置。

## 步骤 1：准备 HAR 抓包（必做）
- 使用浏览器chrome，覆盖完整登录流程：访问登录页、提交登录（成功/失败各一次）、登录后访问用户信息接口或受保护接口。必要时包含静态资源访问，用于白名单。
- 打开“保留日志/Preserve log”，避免跳转丢记录；确保包含请求头、响应体、Set-Cookie。
- 导出 HAR（要包含敏感信息） 放到 `hars/` 目录，并记住目标主机/域名。

## 步骤 2：用 Cursor + 文档 + HAR 生成配置
- 参考文档目录：`零改造引擎规则doc/readme.md`、`lua-resty-expr.md`、`path-syntax.md`、`变量分类说明.md`、`ctx-var.md`、`exposure_*`。
- 选一个最近的示例做模板（如 `examples/10.0.7.20_config.json` 或 `gitlab_config.json`），复制改造。
- 给 Cursor 的提示词示例：
  ```
  1）分析 零改造引擎规则doc目录下所有资料，阅读 HAR: hars/10.0.7.20.har
  2）识别登录接口（URL/Method/Body/Set-Cookie/响应字段 code、success）
  3）识别会话名（Cookie/Token），用户信息接口（URL/Method/字段 data.id/name）
  4）按照引擎规则和样例生成针对该网站的零改造插件 JSON。
  5）不要改动已有文件，输出新文件到 examples/xxx_config.json
  ```

## 步骤 3：校验与确认
1. 运行验证工具（严格模式可选）  
   ```
   python tools/config_validator.py 零改造引擎规则doc/examples/xxx_config.json
   python tools/config_validator.py --strict 零改造引擎规则doc/examples/xxx_config.json
   ```
2. 对照 HAR 手工复核：
   - 登录成功样本：`success_expr` 是否与 HAR 中 code/success/状态码一致；Set-Cookie 是否覆盖。
   - 登录失败样本：`passwd_failed_expr` 是否命中错误返回。
   - 用户信息接口：`success_expr` 是否用到正确的字段（如 `data.id`）；会话 Cookie 名称是否匹配。
3. 白名单检查：静态资源、登录页、健康检查等路径是否与 HAR/站点路径“全等”；确保白名单插件（regex_whiteuri 或空插件组子路由）在认证前执行。
4. 最终保存配置文件路径：`零改造引擎规则doc/examples/xxx_config.json`，便于复用。

## 参考示例
- 已完成样例：`零改造引擎规则doc/examples/10.0.7.20_config.json`（基于 `hars/10.0.7.20.har`）。
  
## 附录：移动端 APP 抓包配置手册
- 目标：让手机 App 的登录全流程流量经过电脑代理，导出 HAR，供规则生成与校验。
- 工具任选：mitmproxy（免费、易导出 HAR）、Charles、HTTP Toolkit、Proxyman、Burp。下面以 mitmproxy/Charles 说明。

### 通用前提
1. 电脑和手机在同一局域网（同一个 Wi‑Fi）。  
2. 电脑启动代理：  
   - mitmproxy：`mitmproxy -w session.mitm`（默认 8080）。  
   - Charles/Proxyman：直接启动，记下监听端口（常用 8888/9090）。  
3. 在手机 Wi‑Fi 设置中手动代理到电脑 IP 与端口。  
4. 在手机浏览器打开 `http://<电脑IP>:<端口>`（Charles 用 `chls.pro/ssl` 或者 下载：
👉 https://www.charlesproxy.com/assets/legacy-ssl/charles.crt）下载安装并信任根证书。 

Android：设置 → 安全 → 加密与凭据 → 安装证书 → CA 证书
iOS：点击文件 → 安装描述文件 → 设置 → 通用 → 关于本机 → 证书信任设置 → 启用完全信任

假如微信小程序使用了ssl双向证书认证，那么需要 使用android模拟器去处理。
https://blog.csdn.net/hrayha/article/details/106862744 绕过ssl pining使用burp抓包微信小程序

5. 打开目标 App，完成“登录成功一次 + 登录失败一次 + 登录后访问用户信息接口”全流程，确保看到请求/响应、Set-Cookie/Token、Body。  
6. 导出 HAR：  
   - mitmproxy：`mitmproxy2har session.mitm > hars/<app>.har`（或直接 `mitmproxy --save-stream-file` 再转换）。  
   - Charles/HTTP Toolkit：菜单导出 HAR。  
7. 将 HAR 放入 `hars/` 目录，命名可读（如 `hars/app_login.har`），再按主流程生成配置。

### Android 注意点
- Android 7+ 默认不信任用户证书：  
  - 模拟器/Root 设备可把 mitmproxy/Charles 证书装到系统证书区；  
  - HTTP Toolkit/Proxyman 提供一键安装辅助；  
  - MIUI/鸿蒙需在“证书安装”里允许该应用信任用户证书。  
- 若 App 走 QUIC/HTTP3，可在代理里禁 QUIC 或用防火墙/ADB 让其回落 HTTPS/1.1。

### iOS 注意点
- 证书安装后，到“设置-通用-关于本机-证书信任设置”里显式信任根证书。  
- 保持代理开关，不要切到蜂窝网络（除非蜂窝也配代理）。  
- ATS/证书锁定的 App 可能仍需绕过（见下）。

### 证书锁定 / SSL Pinning 处理
- 优先使用无 Pin 的调试包/灰度包。  
- 或用 Frida/Objection/LSPosed + JustTrustMe/TrustMeAlready 等模块去除校验；针对 OkHttp/Volley/NSURLSession 可用 Frida 脚本替换校验证书。  
- 若完全无法绕过，只能改用透明网关+DNS/路由劫持并在网关处做解密（成本高，谨慎）。

### 常见问题排查
- 抓不到包：检查手机是否正确配置手动代理，电脑防火墙是否放行端口。  
- HTTPS 解密失败：根证书未被信任或命中 Pin。  
- 只有部分接口出现：App 可能分域名/多进程，确认全部流量走同一代理；必要时禁 QUIC。  
- 导出 HAR 为空：确保代理记录未被清空，导出前先停止会话再导出。

### 抓完后的整理
- 将 HAR 放入 `hars/`，并在 README 的步骤中引用；必要时对敏感信息做脱敏副本。  
- 按主流程验证配置（成功/失败/用户信息接口/白名单）并运行 `tools/config_validator.py`。  