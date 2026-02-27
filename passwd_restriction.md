# Passwd Restriction 插件

密码限制插件，用于检测登录请求中的弱密码，支持多种检测规则。插件在 `rewrite` 阶段进行检测，如果检测到弱密码，会设置标记供登录插件（`exposure_login`）决定是否拦截。只有登录成功且检测到弱密码的请求才记录日志。

## 配置结构

```json
{
  "blacklist": [],
  "whitelist": [],
  "enable_weakpass_dict": false,
  "allow_name_in_passwd": true,
  "min_passwd_length": 0,
  "fetch_vars": {},
  "login_name_var": "",
  "login_passwd_var": "",
  "action": "allow",
  "rejected_conf": {
    "response_code": 403,
    "response_headers": {},
    "response_body": "",
    "response_body_fmt": "",
    "response_body_args": "",
    "response_msg": ""
  },
  "logging_body": false
}
```

## 配置字段说明

### blacklist

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 正则黑名单列表，密码匹配任一规则则视为弱密码。使用 PCRE 正则表达式语法。

**示例**：
```json
{
  "blacklist": ["^123456$", "^password$", "^admin$"]
}
```

### whitelist

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 正则白名单列表，密码必须匹配至少一个规则才允许。使用 PCRE 正则表达式语法。

**示例**：
```json
{
  "whitelist": ["^[A-Za-z0-9@#$%^&+=]{8,}$"]
}
```

### enable_weakpass_dict

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否启用弱密码字典检查。弱密码字典文件路径为 `/opt/tigersec/config/shield-plugins/weakpass.txt`，文件格式为每行一个弱密码，空行和以 `#` 开头的行会被忽略。

### allow_name_in_passwd

- **类型**: `boolean`
- **默认值**: `true`
- **说明**: 是否允许密码包含用户名。如果设置为 `false`，密码中包含用户名会被视为弱密码。

### min_passwd_length

- **类型**: `number`
- **默认值**: `0`（不检查）
- **说明**: 最小密码长度。未配置或设置为 `0` 时不检查密码长度。

### fetch_vars

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 变量提取配置，用于从请求/响应中提取账密。详细配置见 [变量.md](变量.md#fetch_vars-详细格式配置)。

**注意**：插件优先使用 `passwd_capture` 插件捕获的账密，如果未捕获到，则通过 `fetch_vars` 提取。大部分应用的登录请求字段都是加密的， 所以很少用到`fetch_vars`来提取账密明文。

### login_name_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 登录名变量引用，从 `fetch_vars` 中提取的变量名。必须使用 `${变量名}` 格式引用 `fetch_vars` 中定义的私有变量。

支持格式：
- 字符串：`"${username}"`
- 数组：`["${username}", "${user_id}"]` - 按顺序尝试，取第一个非空值

### login_passwd_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 密码变量引用，从 `fetch_vars` 中提取的变量名。格式同 `login_name_var`，必须使用 `${变量名}` 格式。

### action

- **类型**: `string`
- **默认值**: `"allow"`（或未配置）
- **说明**: 弱密码检测到后的行为。
  - `"block"` 或 `"reject"`: 阻断，拒绝登录，根据 `rejected_conf` 配置返回响应，记录日志
  - `"allow"` 或 `""` 或未配置: 放行，仅记录日志
  - `"notify"`: 告警通知用户，根据 `notify_conf` 配置告警通知（TODO: 目前未实现）

### rejected_conf

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 阻断响应配置，当 `action` 为 `"block"` 或 `"reject"` 时使用。

**字段说明**：
- `response_code` (number, 可选) - 拦截请求时的响应码，默认 403
- `response_headers` (table, 可选) - 拦截响应头配置，支持 `$remote_addr`、`$request_uri` 等变量展开。仅处理 `string` 类型的值。支持 `\$` 转义
- `response_body` (string 或 table, 可选) - 拦截响应体配置
  - 如果为 `string` 类型，支持 `$remote_addr`、`$request_uri` 等变量展开
  - 如果为 `table` 类型，会自动进行 JSON 编码后返回
  - 适合 JSON / 纯文本响应，`Content-Type` 可通过 `response_headers` 控制
  - 支持 `\$` 转义，如 `\$remote_addr` 会被转义为字面量 `$remote_addr`
  - **注意**：如果同时配置了 `response_body_fmt`，则 `response_body_fmt` 优先级更高
- `response_body_fmt` (string, 可选) - 拦截响应体格式化字符串，类似 C `printf` 风格，优先级高于 `response_body`
  - 需要配合 `response_body_args` 使用
  - **注意**：`response_body_fmt` 本身不支持 `$var` 变量替换，如需使用变量，请通过 `response_body_args` 传入
- `response_body_args` (string 或 array, 可选) - 配合 `response_body_fmt` 使用，提供格式化参数
  - 如果为 `string` 类型，作为单个参数使用，会进行变量替换
  - 如果为 `array` 类型，数组中的每个元素会按顺序填充到 `response_body_fmt` 的占位符中
  - 如果参数是 `string` 类型，会进行变量替换；其他类型直接使用
- `response_msg` (string, 可选) - 拦截响应消息配置，使用内置 HTML 模板。若未配置 `response_body` 和 `response_body_fmt`，但配置了 `response_msg`，会自动设置 `Content-Type: text/html`。支持 `\$` 转义

### logging_body

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否记录请求体到日志。当设置为 `true` 时，会记录请求体（base64 编码）到日志中。

## 使用示例

### 1. 基本配置（最小长度 + 黑名单）

```json
{
  "min_passwd_length": 8,
  "blacklist": ["^123456$", "^password$", "^admin$"],
  "action": "block",
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "密码强度不符合要求，请使用至少8位字符的强密码"
  }
}
```

### 2. 白名单规则（必须包含大小写字母和数字）

```json
{
  "whitelist": ["^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).{8,}$"],
  "action": "block",
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "密码必须包含大小写字母和数字，且长度至少8位"
  }
}
```

### 3. 启用弱密码字典

```json
{
  "enable_weakpass_dict": true,
  "min_passwd_length": 8,
  "action": "block",
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "密码过于简单，请使用更复杂的密码"
  }
}
```

### 4. 禁止密码包含用户名

```json
{
  "allow_name_in_passwd": false,
  "min_passwd_length": 8,
  "action": "block",
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "密码不能包含用户名"
  }
}
```

### 5. 从请求中提取账密

```json
{
  "fetch_vars": {
    "username": "$post_arg_username",
    "password": "$post_arg_password"
  },
  "login_name_var": "${username}",
  "login_passwd_var": "${password}",
  "min_passwd_length": 8,
  "blacklist": ["^123456$"],
  "action": "block",
  "rejected_conf": {
    "response_code": 403
  }
}
```

### 6. 仅记录日志，不拦截

```json
{
  "min_passwd_length": 8,
  "blacklist": ["^123456$"],
  "action": "allow",
  "logging_body": true
}
```

## 与其它插件的关系

`passwd_restriction` 插件需要配合其他插件使用：

1. **exposure_login**：
   - `passwd_restriction` 在 `rewrite` 阶段检测弱密码并设置标记
   - `exposure_login` 在 `access` 阶段检查该标记，登录成功时根据配置决定是否拦截

2. **passwd_capture**：
   - `passwd_restriction` 优先使用 `passwd_capture` 插件捕获的账密
   - 如果未捕获到，则通过 `fetch_vars` 从请求/响应中提取账密

## 注意事项

1. **检测顺序**：检测规则按顺序执行（最小长度 → 密码包含用户名 → 黑名单 → 白名单 → 弱密码字典），一旦命中即停止，后续规则不再执行
2. **拦截行为**：
   - 插件本身不执行拦截，由 `exposure_login` 插件根据 `action` 配置执行拦截
   - 当 `action` 为 `"block"` 或 `"reject"` 时，`exposure_login` 会根据 `rejected_conf` 配置返回阻断响应
   - 当 `action` 为 `"allow"` 或未配置时，仅记录日志，不拦截
3. **日志记录**：只有登录成功且检测到弱密码的请求才记录日志
4. **弱密码字典**：字典文件路径为 `/opt/tigersec/config/shield-plugins/weakpass.txt`，需要确保文件存在且可读
5. **账密提取**：优先使用 `passwd_capture` 插件捕获的账密，如果未捕获到，则通过 `fetch_vars` 提取
6. **正则表达式**：黑名单和白名单使用 PCRE 正则表达式语法

## 处理流程

```
登录请求
    ↓
rewrite 阶段
    ├─ 提取账密（优先使用 passwd_capture 捕获的账密）
    ├─ 检测规则（按顺序执行，一旦命中即停止）
    │   ├─ 最小长度检测
    │   ├─ 密码包含用户名检测
    │   ├─ 黑名单检测
    │   ├─ 白名单检测
    │   └─ 弱密码字典检测
    └─ 设置标记（api_ctx.log_passwd_restriction）
         ↓
exposure_login (access 阶段)
    ├─ 登录成功 → 检查弱密码标记
    │   ├─ 存在标记 → 设置 success = true
    │   ├─ action == "block" 或 "reject" → 返回阻断响应（根据 rejected_conf 配置）
    │   └─ action == "allow" 或未配置 → 继续处理
    └─ 登录失败 → 不处理弱密码标记
         ↓
log 阶段
    └─ 登录成功且检测到弱密码 → 记录日志
```
