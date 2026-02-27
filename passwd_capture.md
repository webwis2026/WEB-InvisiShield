# Passwd Capture 插件

账密捕获插件，捕获登录时输入框输入的账密信息。插件通过在前端页面注入 JavaScript 脚本来捕获用户输入的账密信息，并将捕获的账密加密后存储到 Cookie 中。在登录请求（POST）时，插件从 Cookie 中提取并解密账密信息，供其他插件（如 `passwd_restriction`、`passwd_bruteforce`）使用。

## 配置结构

```json
{
  "get": true,
  "set": false,
  "uri_pattern": "",
  "username_selector": "",
  "password_selector": "",
  "reject_uncaptured": false,
  "rejected_conf": {
    "response_code": 403,
    "response_headers": {},
    "response_body": "",
    "response_body_fmt": "",
    "response_body_args": "",
    "response_msg": ""
  }
}
```

## 配置字段说明

### get

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否获取捕获的账密，用于 `rewrite` 阶段从 Cookie 中提取账密。
- **使用场景**: 在登录接口（POST）上配置，用于提取捕获的账密。

### set

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否注入账密捕获脚本，用于 `header_filter` 和 `body_filter` 阶段注入 JS 脚本。
- **使用场景**: 在登录页面（GET）上配置，用于注入捕获脚本。

### uri_pattern

- **类型**: `string`
- **默认值**: 未配置
- **说明**: JS脚本根据该配置进一步匹配包含输入框的登录页。该配置会传递给前端JS脚本，用于在特定URL模式下启用账密捕获功能。

### username_selector

- **类型**: `string`
- **默认值**: 未配置
- **说明**: 自定义用户名输入框 CSS 选择器（JS 脚本使用，为空则使用默认选择器）。

**默认选择器**：包含多种常见选择器，如 `input[name*="user"]`、`input[type="email"]`、`#username` 等。

### password_selector

- **类型**: `string`
- **默认值**: 未配置
- **说明**: 自定义密码输入框 CSS 选择器（JS 脚本使用，为空则使用默认选择器）。

**默认选择器**：包含多种常见选择器，如 `input[name*="pass"]`、`input[type="password"]`、`#password` 等。

### reject_uncaptured

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否阻断未捕获到账密时的请求。
  - `true`: 阻断未捕获到账密的请求（需要配置 `rejected_conf` 响应相关字段）
  - `false` 或未配置: 不阻断（即使配置了 `rejected_conf` 也不阻断）

### rejected_conf

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 拦截响应配置（`reject_uncaptured` 为 `true` 时使用）。

**字段说明**：
- `response_code` (number, 可选) - 未捕获到账密时的响应码，默认 403
- `response_headers` (table, 可选) - 响应头配置，支持 `$remote_addr`、`$request_uri` 等变量展开。仅处理 `string` 类型的值。支持 `\$` 转义
- `response_body` (string 或 table, 可选) - 响应体配置
  - 如果为 `string` 类型，支持 `$remote_addr`、`$request_uri` 等变量展开
  - 如果为 `table` 类型，会自动进行 JSON 编码后返回
  - 适合 JSON / 纯文本响应，`Content-Type` 可通过 `response_headers` 控制
  - 支持 `\$` 转义，如 `\$remote_addr` 会被转义为字面量 `$remote_addr`
  - **注意**：如果同时配置了 `response_body_fmt`，则 `response_body_fmt` 优先级更高
- `response_body_fmt` (string, 可选) - 响应体格式化字符串，类似 C `printf` 风格，优先级高于 `response_body`
  - 需要配合 `response_body_args` 使用
  - **注意**：`response_body_fmt` 本身不支持 `$var` 变量替换，如需使用变量，请通过 `response_body_args` 传入
- `response_body_args` (string 或 array, 可选) - 配合 `response_body_fmt` 使用，提供格式化参数
  - 如果为 `string` 类型，作为单个参数使用，会进行变量替换
  - 如果为 `array` 类型，数组中的每个元素会按顺序填充到 `response_body_fmt` 的占位符中
  - 如果参数是 `string` 类型，会进行变量替换；其他类型直接使用
- `response_msg` (string, 可选) - 响应消息配置，使用内置 HTML 模板。若未配置 `response_body` 和 `response_body_fmt`，但配置了 `response_msg`，会自动设置 `Content-Type: text/html`。支持 `\$` 转义

## 使用示例

### 1. 基本配置（登录页面注入 + 登录接口提取）

**登录页面配置**（GET `/login`）：
```json
{
  "set": true,
  "username_selector": "#username",
  "password_selector": "#password"
}
```

**登录接口配置**（POST `/api/login`）：
```json
{
  "get": true
}
```

### 2. 自定义选择器

```json
{
  "set": true,
  "username_selector": "input[name='email']",
  "password_selector": "input[type='password']"
}
```

### 3. 未捕获到账密时拦截

```json
{
  "get": true,
  "reject_uncaptured": true,
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "请使用浏览器登录"
  }
}
```

### 4. 仅注入脚本（不提取）

```json
{
  "set": true
}
```

### 5. 仅提取账密（不注入脚本）

```json
{
  "get": true
}
```

## 与其它插件的关系

`passwd_capture` 插件为其他插件提供捕获的账密信息：

1. **passwd_restriction**：
   - `passwd_capture` 捕获的账密会设置到 `api_ctx.login_captured_loginname` 和 `api_ctx.login_captured_password`
   - `passwd_restriction` 优先使用捕获的账密进行弱密码检测

2. **passwd_bruteforce**：
   - `passwd_capture` 捕获的登录名会设置到 `api_ctx.login_captured_loginname`
   - `passwd_bruteforce` 优先使用捕获的登录名作为限流 key

3. **exposure_login**：
   - 在记录登录日志时，如果无法从 `fetch_vars` 中提取到 `user_id`，可能会使用 `api_ctx.login_captured_loginname` 作为日志中的用户标识

## 注意事项

1. **Cookie 名称**：捕获的账密存储在 `tigersec_upsc` Cookie 中，插件会自动管理改 Cookie
2. **加密方式**：支持 RSA 加密，使用 SHA-1 或 SHA-256（由前端 JS 脚本决定）
3. **注入条件**：脚本注入需要满足以下条件：
   - GET 请求
   - Content-Type 为 `text/html`
   - 无 Content-Encoding（不支持压缩响应）
   - 已代理转发
4. **提取时机**：仅在 POST 请求时提取账密
5. **拦截逻辑**：只有 `reject_uncaptured` 为 `true` 时才会阻断未捕获到账密的请求（通常用于防止非浏览器登录）
6. **脚本位置**：注入的脚本会插入到 `</head>`、`</body>` 标签前，或 `</html>` 标签后
7. **默认选择器**：如果不配置 `username_selector` 和 `password_selector`，会使用默认选择器，支持多种常见的输入框选择器

## 处理流程

### 注入脚本流程（set=true）

```
GET 登录页面
    ↓
before_proxy 阶段
    └─ 清理可能存在的 cookie（如果未配置 get 和 set）
         ↓
header_filter 阶段
    ├─ 检查是否支持注入（GET、text/html、无压缩、已代理）
    └─ 设置标记（api_ctx.do_passwd_capture = true）
         ↓
body_filter 阶段
    ├─ 获取完整响应体
    └─ 注入 JS 脚本（</head>、</body> 前或 </html> 后）
         ↓
用户输入账密 → JS 加密 → 存储到 tigersec_upsc Cookie
```

### 提取账密流程（get=true）

```
POST 登录请求
    ↓
rewrite 阶段
    ├─ 从 tigersec_upsc Cookie 提取账密
    ├─ URI 解码 + Base64 解码
    ├─ RSA 解密（SHA-1 或 SHA-256）
    ├─ 设置到 api_ctx（login_captured_loginname、login_captured_password）
    ├─ 删除 Cookie
    └─ 未捕获到账密且配置 rejected_conf → 返回拦截响应
         ↓
其他插件使用捕获的账密（passwd_restriction、passwd_bruteforce）
```
