# Exposure User 插件

暴露面用户信息获取插件，支持发起多个子请求来获取用户身份信息。该插件由 `exposure_auth` 和 `exposure_login` 插件调用，当本地 session 匹配失败时，通过配置的子请求验证应用本身的登录状态并获取用户身份信息（user_id、user_name）。插件支持多个子请求按顺序执行、条件执行、变量传递、动态参数等多种功能。

**重要说明**：`exposure_user` 是特殊插件，被其他插件调用，不需要在请求执行的插件组中配置绑定。必须在应用作用域范围内的 `plugin_confs` 节点下配置。

## 配置位置

`exposure_user` 插件配置必须在应用配置的 `plugin_confs` 节点下：

```json
{
  "plugins": [...],
  "sub_routes": [...],
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_grafana_session",
      "sub_requests": [
        {
          "name": "get_user",
          "uri": "/api/user",
          "method": "GET",
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "login"},
            "user_name": {"source": "response_body", "parser": "json", "field": "login"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user.user_id}",
      "user_name_var": "${get_user.user_name}"
    }
  }
}
```

**注意**：
- 不要在 `plugins` 或 `sub_routes` 的 `plugins` 数组中配置 `exposure_user`
- 必须在 `plugin_confs` 节点下配置，键名为 `"exposure_user"`

## 配置说明

### 基本配置

在应用配置的 `plugin_confs` 节点下配置：

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_token",
      "sub_requests": [
        {
          "name": "get_user",
          "uri": "/api/check",
          "method": "GET",
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.user_id"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.user_name"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user.user_id}",
      "user_name_var": "${get_user.user_name}"
    }
  }
}
```

### 完整配置示例

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_token",
      "sub_requests": [
        {
          "name": "check_login",
          "uri": "/api/check",
          "method": "POST",
          "headers": {
            "Authorization": "Bearer $http_authorization"
          },
          "body": "{\"token\": \"$cookie_token\"}",
          "fetch_vars": {
            "is_logged_in": {"source": "response_body", "parser": "json", "field": "data.is_logged_in"},
            "session_id": {"source": "response_body", "parser": "json", "field": "data.session_id"}
          },
          "success_expr": ["AND",
            ["${upstream_status}", "==", 200],
            ["${is_logged_in}", "==", "true"]
          ]
        },
        {
          "name": "get_user_info",
          "uri": "/api/user",
          "method": "GET",
          "headers": {
            "X-Session-ID": "${ check_login.session_id }"
          },
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.user.id"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.user.name"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user_info.user_id}",
      "user_name_var": "${get_user_info.user_name}",
      "cache_succ_ttl": 300,
      "cache_fail_ttl": 120,
      "cache_size": 2048,
      "connection_keepalive_timeout": 600000,
      "connection_keepalive_pool": 20
    }
  }
}
```

## 配置字段说明

### sub_requests (必需)

子请求配置数组，支持多个子请求按顺序执行。

#### 基本字段

- `name` (必需) - 子请求名称，用于标识该子请求，可通过 `${ name.xxx }` 或 `user_id_var` 引用其提取的变量
- `desc` (可选) - 子请求描述，用于说明该子请求的用途
- `uri` (必需) - 子请求的URI，支持动态参数语法
- `method` (可选) - HTTP方法，默认根据是否有body自动判断（有body为POST，否则为GET）
- `query` (可选) - 查询参数对象，支持动态参数语法
- `headers` (可选) - 请求头对象，支持动态参数语法

**注意**：以下请求头会自动设置，无需在配置中重复指定：
- `Cookie` - 自动从当前请求的 Cookie 中获取（不包含 WISID）
- `X-Real-IP` - 自动设置为客户端真实 IP
- `X-Forwarded-For` - 自动设置为客户端真实 IP
- `Host` - 自动设置为上游服务的 Host
- `User-Agent` - 自动从当前请求的 User-Agent 中获取

如果配置了 `headers`，会与默认请求头合并，配置的值会覆盖默认值。
- `body` (可选) - 请求体，支持动态参数语法
- `exec_expr` (可选) - 条件表达式，使用 `lua-resty-expr` 语法，控制该子请求是否执行。详细语法见 [条件表达式.md](条件表达式.md)
  - **使用场景**：根据当前请求条件（如 User-Agent）判定访问平台，针对不同平台发起不同的子请求
  - **可用变量**：系统变量（`api_ctx.var`），必须使用 `$xxx` 格式引用
  - **示例**：`[["$http_user_agent", "~~", "Mobile"]]` 匹配移动端请求
- `connect_timeout` (可选) - 连接超时时间（毫秒），默认使用路由的 `upstream.opts.connect_timeout` 或 10000
- `send_timeout` (可选) - 发送超时时间（毫秒），默认使用路由的 `upstream.opts.send_timeout` 或 60000
- `read_timeout` (可选) - 读取超时时间（毫秒），默认使用路由的 `upstream.opts.read_timeout` 或 120000

#### 变量提取

- `fetch_vars` (可选) - 从响应中提取变量的配置，格式同 exposure_login 的 fetch_vars。详细路径语法见 [path-syntax.md](path-syntax.md)
- `success_expr` (必需) - 使用 `lua-resty-expr` 表达式判定子请求是否成功。详细语法见 [条件表达式.md](条件表达式.md)
  - **可用变量**：响应内置变量（`upstream_status`、`header_xxx_xxx`）和 `fetch_vars` 中提取的变量
  - **注意**：引用 `fetch_vars` 中提取的变量必须使用 `${变量名}` 格式，响应内置变量也需要使用 `${变量名}` 格式

### user_id_var (推荐配置)

从哪个子请求的哪个变量中提取 `user_id`。支持字符串或数组格式。

**说明**：通常需要配置此字段。如果无法从子请求中提取到用户信息，可以通过数组格式中的常量字符串作为 fallback 值。

**注意**：必须使用子请求的 `name` 来引用变量，不支持索引（因为子请求可能条件执行，索引不可靠）。

**字符串格式**：
- `${sub_name.xxx}` - 如 `${get_user.user_id}` 表示从名为 `get_user` 的子请求中提取 `user_id` 变量
- `${sub_name.xxx[*]}` - 如 `${get_user.user_ids[*]}` 表示从数组中提取第一个非空值

**数组格式**：
按顺序尝试多个路径，取第一个非空值：

```json
{
  "user_id_var": ["${get_user.user_id}", "${backup.user_id}"]
}
```

变量可以从以下位置提取：
- 自定义提取的变量（通过 `fetch_vars` 配置提取的，如 `user_id`、`user_name`）
- `upstream_status` - 上游（应用）响应状态码（内置变量）
- `header_xxx_xxx` - 响应头（内置变量），格式为 `header_<header_name>`，header 名称转小写，`-` 替换为 `_`
  - 例如：`header_content_type`、`header_set_cookie`、`header_x_auth_token`

### user_name_var (推荐配置)

从哪个子请求的哪个变量中提取 `user_name`，格式同 `user_id_var`。

**说明**：通常需要配置此字段。如果无法从子请求中提取到用户信息，可以通过数组格式中的常量字符串作为 fallback 值。

**注意**：`user_id_var` 和 `user_name_var` 支持 fallback 值。在数组格式中，如果某个元素不包含 `${}` 语法，则作为 fallback 值使用。fallback 值必须是数组中的最后一个元素：

```json
{
  "user_id_var": ["${get_user.user_id}", "${backup.user_id}", "unknown"],
  "user_name_var": ["${get_user.user_name}", "anonymous"]
}
```

上述配置表示：
- `user_id_var`：优先从 `get_user.user_id` 提取，如果提取不到则尝试 `backup.user_id`，如果还是提取不到则使用 `"unknown"` 作为 fallback
- `user_name_var`：优先从 `get_user.user_name` 提取，如果提取不到则使用 `"anonymous"` 作为 fallback

### key_name (必需)

应用本身的认证key名称，用于在发送子请求前检查请求是否携带认证信息。如果请求未携带此key或未配置 `key_name`，将直接返回失败，不发送子请求。

**支持的格式**：
- `cookie_token` - Cookie 中的 token
- `http_authorization` - 请求头 Authorization
- `http_x_auth_token` - 请求头 X-Auth-Token
- `["cookie_token", "http_authorization"]` - 多个候选 key，按顺序尝试
- 其他 `api_ctx.var` 中可用的变量名

**示例**：
```json
{
  "key_name": "cookie_token"
}
```

或使用多个候选 key：

```json
{
  "key_name": ["cookie_token", "http_authorization"]
}
```

**注意事项**：
- **必需配置**：必须配置 `key_name`，否则无法获取认证值，不会发起子请求
- 请求必须携带对应的认证信息，否则不会发送子请求
- 支持从请求和响应中合并提取（如果存在 res，会从响应 Set-Cookie 和 headers 中提取）

### cache_succ_ttl (可选)

用户信息成功结果缓存时间（秒），默认 300 秒（5分钟）。用于防止频繁请求后台应用接口。

**示例**：
```json
{
  "cache_succ_ttl": 600
}
```

### cache_fail_ttl (可选)

用户信息失败结果缓存时间（秒），默认 120 秒（2分钟）。用于防止频繁请求后台应用接口。

**示例**：
```json
{
  "cache_fail_ttl": 60
}
```

### cache_size (可选)

用户信息缓存大小（条数），默认 2048。用于限制缓存的最大条目数，超过限制时会自动淘汰最久未使用的条目。

**注意**：缓存大小在模块加载时初始化，配置修改后需要重新加载模块才能生效。每个路由有独立的缓存实例。

**示例**：
```json
{
  "cache_size": 4096
}
```

### cache_key_with_ip (可选)

缓存key是否包含IP地址，默认 `false`。

- `true`: 缓存key格式为 `IP:value`，不同IP的相同认证值会分别缓存
- `false`: 缓存key格式为 `value`，相同认证值共享缓存

**示例**：
```json
{
  "cache_key_with_ip": true
}
```

### connection_keepalive_timeout (可选)

HTTP 连接池的空闲超时时间（毫秒），默认 600000（10分钟）。

### connection_keepalive_pool (可选)

HTTP 连接池的最大连接数，默认 20。


## 使用示例

### 示例 1：单个子请求获取用户信息

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_token",
      "sub_requests": [
        {
          "name": "get_user",
          "uri": "/api/userinfo",
          "method": "GET",
          "headers": {
            "Cookie": "$http_cookie"
          },
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.id"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.name"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user.user_id}",
      "user_name_var": "${get_user.user_name}"
    }
  }
}
```

### 示例 2：两个子请求，第二个使用第一个的结果

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "http_authorization",
      "sub_requests": [
        {
          "name": "validate_token",
          "uri": "/api/validate",
          "method": "POST",
          "headers": {
            "Authorization": "$http_authorization"
          },
          "fetch_vars": {
            "valid": {"source": "response_body", "parser": "json", "field": "data.valid"},
            "user_token": {"source": "response_body", "parser": "json", "field": "data.token"}
          },
          "success_expr": ["AND",
            ["${upstream_status}", "==", 200],
            ["${valid}", "==", "true"]
          ]
        },
        {
          "name": "get_user",
          "uri": "/api/user",
          "method": "GET",
          "headers": {
            "Authorization": "Bearer ${ validate_token.user_token }"
          },
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.id"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.name"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user.user_id}",
      "user_name_var": "${get_user.user_name}"
    }
  }
}
```

### 示例 3：条件执行子请求

针对不同平台使用不同的认证接口：

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_token",
      "sub_requests": [
        {
          "name": "web_auth",
          "desc": "Web端认证",
          "exec_expr": [["$http_user_agent", "!", "~~", "Mobile"]],
          "uri": "/api/web/check",
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.user_id"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.user_name"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        },
        {
          "name": "mobile_auth",
          "desc": "移动端认证",
          "exec_expr": [["$http_user_agent", "~~", "Mobile"]],
          "uri": "/api/mobile/check",
          "fetch_vars": {
            "user_id": {"source": "response_body", "parser": "json", "field": "data.uid"},
            "user_name": {"source": "response_body", "parser": "json", "field": "data.nickname"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": ["${web_auth.user_id}", "${mobile_auth.user_id}"],
      "user_name_var": ["${web_auth.user_name}", "${mobile_auth.user_name}"]
    }
  }
}
```

### 示例 4：从数组中提取第一个非空值

```json
{
  "plugin_confs": {
    "exposure_user": {
      "key_name": "cookie_token",
      "sub_requests": [
        {
          "name": "get_user",
          "uri": "/api/users",
          "fetch_vars": {
            "user_ids": {"source": "response_body", "parser": "json", "field": "data.users[*].id"}
          },
          "success_expr": [["${upstream_status}", "==", 200]]
        }
      ],
      "user_id_var": "${get_user.user_ids[*]}"
    }
  }
}
```

## 动态参数语法

### 引用当前请求变量

- `$xxx` - 直接引用系统变量

常用变量：
- `$http_authorization` - 请求头 Authorization
- `$http_x_auth_token` - 请求头 X-Auth-Token
- `$cookie_token` - Cookie 中的 token
- `$remote_addr` - 客户端 IP
- `$host` - 请求 Host

完整的请求变量列表见 [变量.md](变量.md)。

例如：
```json
{
  "headers": {
    "Authorization": "$http_authorization",
    "X-Real-IP": "$remote_addr"
  }
}
```

### 引用子请求提取的变量

- `${ name.xxx }` - 引用名为 `name` 的子请求中提取的变量 `xxx`

例如：
```json
{
  "uri": "/api/user/${ check_login.user_id }",
  "headers": {
    "X-Session-ID": "${ check_login.session_id }"
  }
}
```

### 执行 Lua 代码

**暂未实现**：当前版本不支持使用 `{% lua_code %}` 语法执行 Lua 代码构建动态请求体。

## 与其它插件的关系

`exposure_user` 插件被 `exposure_auth` 和 `exposure_login` 插件调用：

1. **exposure_auth**：
   - 当本地 session 匹配失败时，调用 `exposure_user.run()` 获取用户信息
   - 获取到用户信息后，调用 `exposure_session.save()` 保存会话

2. **exposure_login**：
   - 当登录成功但无法从 `fetch_vars` 中提取到用户信息时，调用 `exposure_user.run()` 获取用户信息
   - 获取到用户信息后，调用 `exposure_session.save()` 保存会话

## 注意事项

1. **子请求名称必须唯一**：每个子请求的 `name` 必须唯一，用于后续引用
2. **条件执行**：如果配置了 `exec_expr`，只有表达式为真时才执行该子请求
3. **顺序执行**：子请求按配置顺序依次执行，后续子请求可以使用前面子请求的结果
4. **失败处理**：如果某个子请求失败（`success_expr` 为假），整个流程会失败
5. **变量引用格式**：`user_id_var` 和 `user_name_var` 必须使用 `${sub_name.xxx}` 格式引用，不支持索引
6. **缓存机制**：插件会缓存成功和失败的结果，避免频繁请求后台应用接口
7. **动态参数**：支持 `$xxx`、`${name.xxx}` 两种动态参数语法（Lua 代码执行暂未实现）

## 处理流程

```
调用 exposure_user.run()
    ↓
检查 key_name（如果配置）
    ├─ 未配置 → 直接发送子请求
    └─ 已配置 → 检查请求是否携带认证信息
        ├─ 未携带 → 返回失败
        └─ 已携带 → 继续
             ↓
检查缓存（基于认证值）
    ├─ 缓存命中 → 返回缓存结果
    └─ 缓存未命中 → 继续
         ↓
按顺序执行子请求
    ├─ 检查 exec_expr（如果配置）
    ├─ 处理动态参数（$xxx、${name.xxx}）
    ├─ 发起子请求
    ├─ 提取变量（fetch_vars）
    └─ 判定成功（success_expr）
         ├─ 失败 → 返回失败，缓存失败结果
         └─ 成功 → 继续下一个子请求
              ↓
所有子请求成功
    ├─ 提取用户信息（user_id_var、user_name_var）
    └─ 返回用户信息，缓存成功结果
```
