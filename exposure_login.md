# Exposure Login 插件

暴露面登录接口插件，用于处理登录请求。插件将登录请求代理转发到后端服务，从请求和响应中提取变量（支持 JSON、XML、正则等多种解析方式），使用表达式判定登录成功/失败，并在登录成功时保存会话并设置 Cookie。插件还支持记录登录请求日志，并可与 `passwd_restriction`、`passwd_bruteforce` 等插件协作，实现弱密码检测和暴力破解防护。

## 配置结构

```json
{
  "fetch_vars": {},
  "user_id_var": "",
  "user_name_var": "",
  "failure_msg_var": "",
  "success_expr": [],
  "passwd_failed_expr": [],
  "log_login_expr": [],
  "save_session": false,
  "log_method": "password",
  "inspect_content": {
    "enable": false,
    "reject": false,
    "target_vars": [],
    "rules": [],
    "response_code": 403,
    "response_headers": {},
    "response_body": "",
    "response_body_fmt": "",
    "response_body_args": "",
    "response_msg": ""
  }
}
```

**注意**：`exposure_login` 插件依赖 `exposure_session` 和 `exposure_user` 插件来管理会话。当配置 `save_session = true` 时，需要确保 `exposure_session` 插件已正确配置。

## 配置字段说明

### fetch_vars

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 定义要提取的变量，key 为变量名（可以是任意名称），value 为提取配置。提取的变量存储在插件自身的变量集合中，可以在 `success_expr`, `passwd_failed_expr`,`user_id_var`,`user_name_var` 中使用。这些变量是插件私有的，不会注册到 `ctx.var` 中。

支持两种配置格式：

#### 简单格式（字符串）

```json
{
  "fetch_vars": {
    "username": "$post_arg_username",
    "user_id": "$arg_user_id",
    "remote_addr": "$remote_addr"
  }
}
```

格式：`$variable_name`（仅支持以'$'引用系统变量），例如:
- `$remote_addr` - 对端IP
- `$post_arg_username` - 引用 POST 参数（注意：使用下划线，不是点号）
- `$arg_user_id` - 引用查询参数
- `$http_x_forwarded_for` - 引用请求头（注意：使用下划线，不是横线）

完整的系统变量列表见 [变量.md](变量.md#系统变量列表)
#### 详细格式（对象）

支持从响应头、响应 body 中提取变量，并支持 JSON、XML、正则等多种解析器。

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_body",
      "field": "data.user.id",
      "parser": "json"
    }
  }
}
```

**字段说明**：
- `source` (必需) - 提取源：`var_ref`（引用系统变量）、`request_body`（请求体）、`response_header`（响应头）、`response_body`（响应体）
- `field` (必需) - 字段名或路径，根据 `source` 和 `parser` 类型使用不同的路径格式
- `parser` (可选) - 解析器类型：`json`、`xml` 或 `regex`，仅当 `source` 为 `request_body` 或 `response_body` 时使用
- `regex` (可选) - 正则表达式，用于对提取的值进行二次过滤（当 `source` 为 `var_ref` 或 `response_header` 时使用）
- `options` (可选) - 正则表达式选项，如 `"jo"`（仅当使用 `regex` 时）
- `select` (可选) - 值选择器，用于从数组/table中选择值
  - `type`: `"index"`（按索引选择）、`"first"`（取第一个非空值）、`"join"`（连接数组）、`"json"`（JSON编码）
  - `index`: 索引值（当 `type` 为 `"index"` 时）
  - `sep`: 分隔符（当 `type` 为 `"join"` 时）
- `cast` (可选) - 类型转换，可选值：`"string"`、`"number"`

详细配置说明和更多示例见 [变量.md](变量.md#fetch_vars-详细格式配置)。

### user_id_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 从 `fetch_vars` 中提取的变量名，用于设置 `api_ctx.matched_user.id`。必须使用 `${变量名}` 格式引用 `fetch_vars` 中定义的私有变量。

支持格式：
- 字符串：`"${user_id}"` 或 `"${user_ids}[*]"`
- 数组：`["${user_id}", "${sub_user_id}"]` - 按顺序尝试，取第一个非空值

### user_name_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 从 `fetch_vars` 中提取的变量名，用于设置 `api_ctx.matched_user.name`。格式同 `user_id_var`，必须使用 `${变量名}` 格式。

**注意**: 如果配置了`"save_session":true`，则需要获取到 `user_id` 和 `user_name` 才能调用 `exposure_session` 插件保存会话。此时会按以下顺序尝试获取用户信息：
1. 优先从 `fetch_vars` 中提取（通过 `user_id_var` 和 `user_name_var` 配置）
2. 如果未配置 `user_id_var`/`user_name_var` 或提取失败，则调用 `exposure_user` 插件获取用户信息
3. 如果 `exposure_user` 也获取不到用户信息，则不会保存会话

### failure_msg_var

- **类型**: `string` 或 `array`
- **默认值**: 未配置
- **说明**: 从 `fetch_vars` 中提取的变量名，用于获取登录失败时的错误消息。必须使用 `${变量名}` 格式引用 `fetch_vars` 中定义的私有变量。

支持格式：
- 字符串：`"${error_msg}"` 或 `"${error_messages}[*]"`
- 数组：`["${error_msg}", "${message}"]` - 按顺序尝试，取第一个非空值

**注意**: 当登录失败（`success_expr` 判定为 `false`）时，会从 `fetch_vars` 中提取失败消息并记录到登录日志的 `fail_message` 字段中。

### success_expr

- **类型**: `array`
- **默认值**: 未配置
- **说明**: 使用 `lua-resty-expr` 表达式判定登录请求是否成功。详细语法见 [条件表达式.md](条件表达式.md)。

**可用变量**：
- 响应内置变量：`upstream_status`、`header_content_type`、`header_xxx_xxx` 等
- `fetch_vars` 中提取的变量（必须使用 `${变量名}` 格式引用）

**注意**: 只有配置了`success_expr`变量表达式判定登录成功，才会进一步执行保存会话，弱密码拦截等功能

**示例**：
```json
{
  "success_expr": [
    ["${upstream_status}", "==", 200],
    ["${user_id}", "~=", ""]
  ]
}
```

### passwd_failed_expr

- **类型**: `array`
- **默认值**: 未配置
- **说明**: 使用 `lua-resty-expr` 表达式判定是否账密登录失败，用于生成上下文标记 `api_ctx.count_passwd_bruteforce`。

**可用变量**：同 `success_expr`，仅支持响应内置变量和 `fetch_vars` 中提取的变量，必须使用 `${变量名}` 格式引用。

**注意**: 只有配置了`passwd_failed_expr`变量表达式判定账密登录失败，才会设置标记到上下文，联动`passwd_bruteforce`插件实现暴力破解的计数与拦截。

**示例**：
```json
{
  "passwd_failed_expr": [
    ["${upstream_status}", "==", 401],
    ["${error_code}", "==", "INVALID_PASSWORD"]
  ]
}
```

### save_session

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 登录成功时是否保存会话。当设置为 `true` 时，会调用 `exposure_session.save()` 保存会话到虎盾 portal 并设置 WISID cookie。

### log_method

- **类型**: `string`
- **默认值**: `"password"`
- **说明**: 登录方式，用于标识登录请求的类型。
- **可选值**:
  - `"password"` - 账密登录（默认）
  - `"sso"` - SSO 登录
  - `"qrcode"` - 二维码登录

**注意**: 此字段用于登录日志记录，不影响插件功能逻辑。

### log_login_expr

- **类型**: `array`
- **默认值**: 未配置
- **说明**: 使用 `lua-resty-expr` 表达式判定是否应该记录登录日志。如果未配置，默认记录所有登录请求的日志。

**可用变量**：同 `success_expr`，仅支持响应内置变量和 `fetch_vars` 中提取的变量，必须使用 `${变量名}` 格式引用。

**示例**：
```json
{
  "log_login_expr": [
    ["${upstream_status}", ">=", 200],
    ["${upstream_status}", "<", 300]
  ]
}
```

上述配置表示：只有当响应状态码在 200-299 之间时才记录登录日志。

## 日志记录

`exposure_login` 插件会在 log 阶段自动记录以下日志：

### 登录日志

插件会记录每次登录请求的详细信息，包括：
- 用户信息（`user_id`、`user_name`）
- 登录结果（`success`、`fail_code`、`fail_message`）
- 登录方式（`log_method`）
- 请求信息（IP、User-Agent、时间等）
- 应用和租户信息

**失败消息提取**：当登录失败时，如果配置了 `failure_msg_var`，插件会从 `fetch_vars` 中提取失败消息并记录到 `fail_message` 字段中。

### 告警日志

当 `inspect_content` 内容检测命中规则时，会记录告警日志，包括：
- 检测事件信息（`event`、`action`、`level`、`message`）
- 请求详情（URL、请求头、请求体等）
- 用户和应用信息

**注意**：告警日志仅在内容检测命中时记录，与是否阻断请求无关。

### inspect_content

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 内容检测配置，用于检测响应内容并决定是否阻断请求。

**重要说明**：`inspect_content.rules` 中的具体检测规则**通常不需要在应用插件的 `exposure_login` 配置里手动编写**。实际使用时，这些规则会在 OP / Console 中通过 UI 统一配置，并下发到网关，与应用插件中已有的 `exposure_login.inspect_content` 配置做**字段级别的合并（merge）**，从而生效。

**字段说明**：
- `enable` (boolean, 必需) - 是否启用内容检测
- `reject` (boolean, 可选) - 命中检测规则时是否阻断请求
  - `true`: 阻断请求（需要配置响应相关字段）
  - `false` 或未配置: 不阻断（仅记录日志）
  - **注意**：兼容旧的 `block` 配置字段名。如果同时配置了 `reject` 和 `block`，优先使用 `reject`
- `target_vars` (array, 必需) - 要检测的变量列表，从 `fetch_vars` 中提取的变量名。必须使用 `${变量名}` 格式引用 `fetch_vars` 中定义的私有变量
- `rules` (array, 必需) - 检测规则列表，支持新格式（对象数组）：
  - 每个规则是一个对象，包含以下字段：
    - `name` (string, 可选) - 规则名称，用于日志记录，默认 "unknown"
    - `patterns` (array, 必需) - 正则表达式模式列表，使用 PCRE 正则表达式语法
    - `operator` (string, 可选) - 匹配逻辑，可选值：`"OR"`（默认）或 `"AND"`
      - `"OR"`：任意一个 pattern 匹配即命中规则
      - `"AND"`：所有 pattern 都必须匹配才命中规则
- `response_code` (number, 可选) - 命中后返回的响应码，默认 403
- `response_headers` (table, 可选) - 命中后返回的响应头配置
- `response_body` (string 或 table, 可选) - 命中后返回的响应体配置
  - 如果为 `string` 类型，支持 `$remote_addr`、`$request_uri` 等变量展开
  - 如果为 `table` 类型，会自动进行 JSON 编码后返回
  - **注意**：如果同时配置了 `response_body_fmt`，则 `response_body_fmt` 优先级更高
- `response_body_fmt` (string, 可选) - 响应体格式化字符串，类似 C `printf` 风格，优先级高于 `response_body`
  - 需要配合 `response_body_args` 使用
  - **注意**：`response_body_fmt` 本身不支持 `$var` 变量替换，如需使用变量，请通过 `response_body_args` 传入
- `response_body_args` (string 或 array, 可选) - 配合 `response_body_fmt` 使用，提供格式化参数
  - 如果为 `string` 类型，作为单个参数使用，会进行变量替换
  - 如果为 `array` 类型，数组中的每个元素会按顺序填充到 `response_body_fmt` 的占位符中
  - 如果参数是 `string` 类型，会进行变量替换；其他类型直接使用
- `response_msg` (string, 可选) - 命中后返回的响应消息配置（使用内置 HTML 模板）。若未配置 `response_body` 和 `response_body_fmt`，但配置了 `response_msg`，会自动设置 `Content-Type: text/html`

**注意**：
- 如果要检测整个请求 body，需要在 `fetch_vars` 中提取整个 body
- 检测规则按顺序匹配，一旦命中即停止
- 如果 `reject` 为 `false` 或未配置，即使配置了 `response_code` 也不会阻断请求


## 使用示例

### 1. 从响应 body 的 JSON 中提取用户信息

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_body",
      "field": "data.user.id",
      "parser": "json"
    },
    "username": {
      "source": "response_body",
      "field": "data.user.name",
      "parser": "json"
    }
  },
  "user_id_var": "${user_id}",
  "user_name_var": "${username}",
  "success_expr": [
    ["${upstream_status}", "==", 200],
    ["${user_id}", "~=", ""]
  ],
  "save_session": true
}
```

### 2. 使用简单格式引用变量

```json
{
  "fetch_vars": {
    "remote_addr": "$remote_addr",
    "username": "$post_arg_username",
    "user_id": "$arg_user_id"
  },
  "user_name_var": "username"
}
```

### 3. 从响应 body 使用正则提取

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_body",
      "field": "user_id[=:]([0-9]+)",
      "parser": "regex"
    }
  },
  "user_id_var": "${user_id}"
}
```

### 4. 从响应头中提取并正则过滤

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_header",
      "field": "X-Auth-Token",
      "regex": "user_id:([^,]+)"
    }
  },
  "user_id_var": "${user_id}"
}
```

### 5. 完整的登录流程配置

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_body",
      "field": "data.user.id",
      "parser": "json"
    },
    "username": {
      "source": "var_ref",
      "field": "$post_arg_username"
    },
    "error_code": {
      "source": "response_body",
      "field": "data.error.code",
      "parser": "json"
    },
    "token": {
      "source": "response_header",
      "field": "X-Auth-Token"
    }
  },
  "user_id_var": "${user_id}",
  "user_name_var": "${username}",
  "success_expr": [
    ["${upstream_status}", "==", 200],
    ["${user_id}", "~=", ""],
    ["${error_code}", "==", ""]
  ],
  "passwd_failed_expr": [
    ["${upstream_status}", "==", 401],
    ["${error_code}", "==", "INVALID_PASSWORD"]
  ],
  "failure_msg_var": "${error_msg}",
  "save_session": true,
  "log_method": "password"
}
```

### 6. 内容检测配置示例

```json
{
  "fetch_vars": {
    "response_body": {
      "source": "response_body",
      "field": ".",
      "parser": "json"
    }
  },
  "inspect_content": {
    "enable": true,
    "reject": true,
    "target_vars": ["${response_body}"],
    "rules": [
      {
        "name": "SQL注入检测",
        "patterns": ["('|;)", "(select|insert|update|delete)"],
        "operator": "OR"
      }
    ],
    "response_code": 403,
    "response_msg": "检测到异常响应内容"
  }
}
```

## 与其它插件的关系

`exposure_login` 插件依赖 `exposure_session` 和 `exposure_user` 插件：

1. **exposure_session**：
   - 当 `save_session = true` 时，调用 `exposure_session.save()` 保存会话到虎盾 portal
   - 在 header_filter 阶段设置 WISID cookie
   - 登录成功时会删除旧的 TSID cookie

2. **exposure_user**：
   - 当 `save_session = true` 但无法从 `fetch_vars` 中提取到用户信息时，会调用 `exposure_user.run()` 获取用户信息

3. **passwd_restriction**：
   - 当登录成功且`passwd_restriction`判定为弱密码(设置标记到上下文时) 时, `exposure_login`插件会根据`passwd_restriction`的配置去执行拦截登录请求。

4. **passwd_bruteforce**：
   - 当 `passwd_failed_expr` 判定为真时，会设置标记到上下文，触发 `passwd_bruteforce` 插件计数

5. **passwd_capture**：
   - `exposure_login` 不会直接调用 `passwd_capture` 插件
   - 在记录登录日志时，如果无法从 `fetch_vars` 中提取到 `user_id`，可能会使用 `api_ctx.login_captured_loginname`（由 `passwd_capture` 插件设置到上下文中的值）作为日志中的用户标识

## 处理流程

```
登录请求
    ↓
access 阶段
    ├─ 删除 TSID Cookie
    ├─ 代理转发请求到后端
    ├─ 提取变量（fetch_vars）
    ├─ 提取用户信息（user_id_var、user_name_var）
    ├─ 判定登录成功（success_expr）
    │   ├─ 成功 → 检查弱密码标记（passwd_restriction）
    │   │   ├─ 存在标记且 action == "block" → 返回阻断响应
    │   │   └─ 不存在或 action == "allow" → 保存会话（save_session）
    │   └─ 失败 → 判定账密失败（passwd_failed_expr）
    │       └─ 账密失败 → 设置 count_passwd_bruteforce = true
    └─ 返回响应（设置响应头、返回状态码和 body）
         ↓
    header_filter 阶段
    └─ save_session = true → exposure_session.set_cookie() → 设置 WISID cookie
         ↓
    log 阶段
    └─ 记录登录日志（包含成功/失败状态、用户信息、失败消息等）
```
