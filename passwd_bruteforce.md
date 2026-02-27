# Passwd Bruteforce 插件

账密暴力破解检测插件，用于检测和防护账密暴力破解攻击。插件通过限流机制检测账密暴力破解攻击，使用 `IP:LOGINNAME` 作为限流 key，在时间窗口内统计账密失败的次数，当达到阈值时进行拦截或记录日志。插件需要配合 `exposure_login` 插件使用，依赖登录插件标记账密错误请求。

## 配置结构

```json
{
  "count": 5,
  "time_window": 300,
  "fetch_vars": {},
  "login_name_var": "",
  "block_ip": false,
  "block_ip_duration": 600,
  "block_login": false,
  "rejected_conf": {
    "response_code": 403,
    "response_headers": {},
    "response_body": "",
    "response_body_fmt": "",
    "response_body_args": "",
    "response_msg": ""
  },
  "logging_body": false,
  "max_body_size": 1024,
  "ip_only_limit": false,
  "ip_limit_count": 10,
  "ip_limit_time_window": 300
}
```

## 配置字段说明

### count

- **类型**: `number`
- **必需**: 是
- **说明**: 时间窗口内允许的最大失败次数。当账密失败次数达到此阈值时，会触发拦截或记录日志。

### time_window

- **类型**: `number`
- **必需**: 是
- **说明**: 时间窗口（秒）。在此时间窗口内统计账密失败次数。


### fetch_vars

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 变量提取配置，用于从请求/响应中提取登录名。详细配置见 [变量.md](变量.md#fetch_vars-详细格式配置)。

**注意**：插件优先使用 `passwd_capture` 插件捕获的登录名，如果未捕获到，则通过 `fetch_vars` 提取。

### login_name_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 登录名变量引用，从 `fetch_vars` 中提取的变量名。必须使用 `${变量名}` 格式引用 `fetch_vars` 中定义的私有变量。

支持格式：
- 字符串：`"${username}"`
- 数组：`["${username}", "${user_id}"]` - 按顺序尝试，取第一个非空值

### block_ip

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否开启将 IP 加入黑名单。当达到次数限制时，会将 IP 加入黑名单。

**注意**：
- IP黑名单阻断功能需要配置`ip_restriction`插件实现
- 优先使用 `block_ip` 配置，兼容旧的 `enable_block_ip` 配置（如果 `block_ip` 未配置，会使用 `enable_block_ip` 的值）

### block_ip_duration

- **类型**: `number`
- **默认值**: `600`（10分钟）
- **说明**: 黑名单 IP 的过期时间（秒）。


### block_login

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 达到限流阈值时，是否阻断登录请求。
  - `true`: 阻断登录请求（需要配置 `rejected_conf` 响应相关字段）
  - `false` 或未配置: 不阻断（即使配置了 `rejected_conf` 也不阻断，仅记录日志）

### rejected_conf

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 拦截响应配置（`block_login` 为 `true` 时使用）。

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

### max_body_size

- **类型**: `number`
- **默认值**: `1024`
- **说明**: 请求体最大大小（字节），用于 `logging_body` 时限制读取的 body 大小。

### ip_only_limit

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否同时开启只用 IP 作为 key 的统计。有些攻击场景，攻击者会使用不同的登录名，此时可以使用 IP 作为限流 key。

### ip_limit_count

- **类型**: `number`
- **默认值**: 未配置（使用 `count` 的值）
- **说明**: IP 作为 key 时的限流次数。当 `ip_only_limit` 为 `true` 时，如果未配置 `ip_limit_count` 和 `ip_limit_time_window`，则使用 `count` 和 `time_window` 的值。

### ip_limit_time_window

- **类型**: `number`
- **默认值**: 未配置（使用 `time_window` 的值）
- **说明**: IP 作为 key 时的限流时间窗口（秒）。当 `ip_only_limit` 为 `true` 时，如果未配置 `ip_limit_count` 和 `ip_limit_time_window`，则使用 `count` 和 `time_window` 的值。

## 使用示例

### 1. 基本配置（5分钟内最多5次失败）

```json
{
  "count": 5,
  "time_window": 300,
  "block_login": true,
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "请求过于频繁，请稍后再试"
  }
}
```

### 2. 启用 IP 黑名单

```json
{
  "count": 5,
  "time_window": 300,
  "block_ip": true,
  "block_ip_duration": 1800,
  "block_login": true,
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "IP已被加入黑名单，请稍后再试"
  }
}
```

### 3. 从请求中提取登录名

```json
{
  "count": 5,
  "time_window": 300,
  "fetch_vars": {
    "username": "$post_arg_username"
  },
  "login_name_var": "${username}",
  "block_login": true,
  "rejected_conf": {
    "response_code": 403
  }
}
```

### 4. 记录请求体

```json
{
  "count": 5,
  "time_window": 300,
  "logging_body": true,
  "max_body_size": 2048,
  "block_login": true,
  "rejected_conf": {
    "response_code": 403
  }
}
```

### 5. 仅记录日志，不拦截

```json
{
  "count": 5,
  "time_window": 300,
  "logging_body": true
}
```

### 6. 启用 IP 限流（同时使用 IP+用户名 和 IP 两种限流）

```json
{
  "count": 5,
  "time_window": 300,
  "ip_only_limit": true,
  "ip_limit_count": 10,
  "ip_limit_time_window": 300,
  "block_login": true,
  "rejected_conf": {
    "response_code": 403,
    "response_msg": "请求过于频繁，请稍后再试"
  }
}
```

## 与其它插件的关系

`passwd_bruteforce` 插件需要配合其他插件使用：

1. **exposure_login**：
   - 在 `access` 阶段，`exposure_login` 判定账密错误后，设置 `api_ctx.count_passwd_bruteforce = true`
   - 在 `header_filter` 阶段，`passwd_bruteforce` 检查该标记，如果存在则对账密错误的请求进行计数

2. **passwd_capture**：
   - `passwd_bruteforce` 优先使用 `passwd_capture` 插件捕获的登录名（`api_ctx.login_captured_loginname`）
   - 如果未捕获到，则通过 `fetch_vars`和`login_name_var` 从请求/响应中提取登录名

3. **ip_restriction**：
   - 如果配置了 `block_ip = true` 或 `enable_block_ip = true`，会将达到阈值的 IP 加入 `plugin-ip_restriction-shared-black` 共享字典
   - `ip_restriction` 插件会读取该共享字典进行 IP 拦截

## 注意事项

1. **限流 key**：
   - 默认使用 "IP:LOGINNAME" 作为限流 key，相同 IP 对不同登录名的限流是独立的
   - 如果启用了 `ip_only_limit`，会同时使用 IP 作为限流 key
2. **两阶段处理**：
   - `rewrite` 阶段：判断是否达到阈值（不实际计数）
   - `header_filter` 阶段：对账密错误的请求进行计数（依赖 `exposure_login` 插件标记）
3. **登录名提取**：优先使用 `passwd_capture` 插件捕获的登录名，如果未捕获到，则通过 `fetch_vars` 提取
4. **IP 黑名单**：需要配置 `plugin-ip_restriction-shared-black` 共享字典
5. **计数时机**：只有账密错误的请求才会进行计数，这样可以准确统计暴力破解攻击
6. **日志记录**：只有达到限流阈值的请求才记录日志
7. **阻断行为**：只有 `block_login` 为 `true` 时才会阻断请求，否则仅记录日志


## 处理流程

```
登录请求
    ↓
rewrite 阶段
    ├─ 提取登录名（优先使用 passwd_capture 捕获的登录名）
    ├─ 生成限流 key（conf_type:route_id:client_ip:loginname）
    ├─ 判断是否达到阈值（commit=false，不实际计数）
    └─ 达到阈值 → 设置标记、加入黑名单（可选）、返回拦截响应（可选）
         ↓
exposure_login (access 阶段)
    ├─ 判定账密错误 → 设置 api_ctx.count_passwd_bruteforce = true
    └─ 判定账密正确 → 不设置标记
         ↓
header_filter 阶段
    ├─ 检查 count_passwd_bruteforce 标记
    └─ 存在标记 → 进行计数（commit=true）
         ↓
log 阶段
    └─ 达到阈值 → 记录日志
```
