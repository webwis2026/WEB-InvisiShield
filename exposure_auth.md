# Exposure Auth 插件

通用暴露面收敛认证插件，用于在应用入口统一做会话认证：
- 优先根据已有会话（如 WISID 或应用自身 cookie/header）匹配本地 session
- 若无有效会话，则通过 `exposure_user` 获取用户信息 + 虎盾 httpauth 获取 WISID
- 可按配置在认证失败时放行、返回自定义响应或重定向

## 配置结构

```json
{
  "log_unauthed": false,
  "reject_unauthed": false,
  "log_provider": "",
  "response_code": 403,
  "response_headers": {},
  "response_body": "",
  "response_body_fmt": "",
  "response_body_args": "",
  "response_msg": ""
}
```

**注意**：`exposure_auth` 插件本身不直接配置认证 key，而是通过 `exposure_session` 插件来管理会话。`exposure_session` 插件的配置需要单独配置，包括 `key_name` 和 `cookie` 等字段。

## 配置字段说明

### log_unauthed

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 未认证失败时是否记录一条简化告警日志（通过 `slslog` 发送）。

### log_provider

- **类型**: `string`
- **默认值**: 空（使用当前插件内置告警日志）
- **说明**:
  - 指定其他日志插件名（如 `"file-logger"`, `"tcp-logger"` 等）接管未认证请求的日志
  - 指定的日志插件需要绑定到路由上
  - 其他日志插件可以提供更丰富的功能，例如指定输出流，复杂条件匹配后记录日志，记录完整的body等

### reject_unauthed

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否阻断未认证请求。
  - `true`: 阻断未认证请求（需要配置响应相关字段）
  - `false` 或未配置: 不阻断（即使配置了 `response_code` 也不阻断）

### response_code

- **类型**: `number`
- **默认值**: 未配置
- **说明**: 未认证时响应码（`reject_unauthed` 为 `true` 时使用）。如果未配置，默认使用 403。
  - 响应码范围说明：
    - `300-399`：重定向
    - 其他：阻断

### response_headers

- **类型**: `table`
- **默认值**: 未配置
- **说明**:
  - 认证失败并配置了 `response_code` 时，优先按此表设置响应头
  - 仅处理 `string` 类型的值
  - 支持 `$remote_addr`、`$request_uri` 等变量展开
  - 支持 `\$` 转义，如 `\$remote_addr` 会被转义为字面量 `$remote_addr`

### response_body

- **类型**: `string` 或 `table`
- **默认值**: 未配置
- **说明**:
  - 若配置了 `response_body`，则返回 `(response_code, resolve_var(response_body))`
  - 如果 `response_body` 是 `string` 类型，会进行变量替换后返回
  - 如果 `response_body` 是 `table` 类型，会自动进行 JSON 编码后返回
  - 适合 JSON / 纯文本响应，`Content-Type` 可通过 `response_headers` 控制
  - 支持 `\$` 转义，如 `\$remote_addr` 会被转义为字面量 `$remote_addr`
  - **注意**：如果同时配置了 `response_body_fmt`，则 `response_body_fmt` 优先级更高

### response_body_fmt

- **类型**: `string`
- **默认值**: 未配置
- **说明**:
  - 使用类似 C `printf` 风格的格式化字符串，优先级高于 `response_body`
  - 需要配合 `response_body_args` 使用，`response_body_args` 中的参数会按顺序填充到格式化字符串中
  - **注意**：`response_body_fmt` 本身不支持 `$var` 变量替换，如需使用变量，请通过 `response_body_args` 传入
  - **示例**：`response_body_fmt: "{\"code\":%d,\"message\":\"%s\"}"`，`response_body_args: [403, "$remote_addr"]`

### response_body_args

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**:
  - 配合 `response_body_fmt` 使用，提供格式化参数
  - 如果为 `string` 类型，作为单个参数使用，会进行变量替换
  - 如果为 `array` 类型，数组中的每个元素会按顺序填充到 `response_body_fmt` 的占位符中
  - 如果参数是 `string` 类型，会进行变量替换；其他类型直接使用
  - **示例**：
    - 单个参数：`"$remote_addr"`
    - 多个参数：`["$remote_addr", 403, "Access denied"]`

### response_msg

- **类型**: `string`
- **默认值**: 未配置
- **说明**:
  - 若未配置 `response_body`，但配置了 `response_msg`：
    - 自动设置 `Content-Type: text/html`
    - 使用内置阻断模板 `resp_tmpl.block_response(resolve_var(response_msg))` 构造 HTML 页面
  - 支持 `\$` 转义，如 `\$remote_addr` 会被转义为字面量 `$remote_addr`

## 使用示例

### 1. 标准 WISID cookie 认证 + 失败返回 403 JSON

**exposure_auth 配置**：
```json
{
  "log_unauthed": true,
  "reject_unauthed": true,
  "response_code": 403,
  "response_headers": {
    "Content-Type": "application/json"
  },
  "response_body": "{\"code\":403,\"message\":\"Access denied\"}"
}
```

**或者使用 table 格式的 response_body**：
```json
{
  "log_unauthed": true,
  "reject_unauthed": true,
  "response_code": 403,
  "response_headers": {
    "Content-Type": "application/json"
  },
  "response_body": {
    "code": 403,
    "message": "Access denied"
  }
}
```

**或者使用 response_body_fmt 格式化**：
```json
{
  "log_unauthed": true,
  "reject_unauthed": true,
  "response_code": 403,
  "response_headers": {
    "Content-Type": "application/json"
  },
  "response_body_fmt": "{\"code\":%d,\"message\":\"Access denied from %s\"}",
  "response_body_args": [403, "$remote_addr"]
}
```

### 2. 认证失败重定向到登录页

```json
{
  "reject_unauthed": true,
  "response_code": 302,
  "response_headers": {
    "Location": "https://login.example.com?redirect=$request_uri"
  }
}
```

### 3. 放行未认证请求，记录日志

```json
{
  "log_unauthed": true,
  "reject_unauthed": false
}
```

## 与其它插件的关系

`exposure_auth` 插件依赖 `exposure_session` 和 `exposure_user` 插件：

1. **exposure_session**：
   - 管理会话（WISID 或应用自身的认证 key）
   - 匹配本地 session 缓存
   - 保存会话到虎盾 portal 并获取 WISID
   - 管理 cookie 的设置和清除

2. **exposure_user**：
   - 当本地 session 匹配失败时，调用 `exposure_user.run()` 获取用户信息
   - 通过配置的子请求获取用户的 `user_id` 和 `user_name`
   - 获取到用户信息后，`exposure_auth` 调用 `session:save()` 保存会话

3. **协作流程**：
   - `exposure_auth` → `exposure_session.open()` → 匹配本地 session
   - 如果匹配失败 → `exposure_user.run()` → 获取用户信息
   - 获取用户信息后 → `exposure_session.save()` → 保存会话到虎盾 portal
   - 在 header_filter 阶段 → `exposure_session.set_cookie()` → 设置 WISID cookie


## 处理流程

```
请求
    ↓
rewrite 阶段
    ├─ OPTIONS 请求 → 直接放行
    ├─ 已有会话匹配
    │   ├─ exposure_session.open() → 匹配本地 session
    │   ├─ 匹配成功 → 设置 api_ctx.matched_user → 返回
    │   └─ 匹配失败 → 继续
    └─ 无会话时获取用户信息
        ├─ exposure_user.run() → 获取用户信息
        ├─ 获取失败 → 记录日志 → 返回响应（如果配置 reject_unauthed）
        └─ 获取成功 → session:set_data() → session:save() → 设置 api_ctx.matched_user
             ↓
    header_filter 阶段
    └─ 存在 exposure_session 且 should_set_cookie() → 设置 WISID cookie
             ↓
    log 阶段
    └─ 存在 log_unauthed_request → 记录日志
```
