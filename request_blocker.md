# Request Blocker 插件

请求内容检测插件，用于检测和阻断危险的请求内容（主要是请求体，也支持请求头检测）。插件采用两级过滤机制：首先基于系统变量进行快速过滤，然后基于自定义提取的变量进行内容检测。

**重要说明**：在实际使用中，`request_blocker` 的规则通常通过 OP 平台的 UI 界面统一配置并下发到网关，**一般不需要在应用的 JSON 配置（如 `gw_configures.plugin_confs`）中手动编写规则**。本文件中的配置结构和示例主要用于理解插件能力和便于调试。

## 检测流程

```
元信息（name / event / level / message）
  ↓
Gate 1：exec_expr（系统变量，快速过滤）
  ↓
Guard：max_body_size（请求体大小检查）
  ↓
Prepare：fetch_vars（自定义变量提取）
  ↓
Gate 2：success_expr（自定义变量，内容检测）
  ↓
Act：reject / log
```

## 配置结构

```json
{
  "excludes": [],
  "rules": [],
  "rejected_msg": ""
}
```

## 配置字段说明

### excludes

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 排除规则列表，匹配排除规则的请求将跳过检测。每个排除规则至少需要配置 `host` 或 `uris` 之一。

**排除规则字段**：
- `host` (可选) - 精确匹配的 host，如果未配置则匹配所有 host
- `uris` (可选) - URI 正则匹配列表，使用 PCRE 正则表达式语法。如果未配置但配置了 `host`，则匹配该 host 的所有 URI

**示例**：
```json
{
  "excludes": [
    {
      "host": "example.com",
      "uris": ["^/api", "/xd"]
    }
  ]
}
```

### rules

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 检测规则列表，按顺序匹配，命中第一个规则后停止匹配。

**规则字段**：

#### name

- **类型**: `string`
- **必需**: 是
- **说明**: 规则名称，用于日志记录和告警。

#### reject

- **类型**: `boolean`
- **默认值**: `false`
- **说明**: 是否阻断请求。`true` 表示命中规则时阻断请求，`false` 表示仅记录日志不阻断。

#### alert

- **类型**: `table`
- **默认值**: 未配置
- **说明**: 告警配置。

**alert 字段**：
- `event` (可选) - 告警事件名称，默认使用规则名称
- `level` (可选) - 告警等级：`INFO`、`LOW`、`MEDIUM`、`HIGH`、`CRITICAL`，默认：`HIGH`
- `message` (可选) - 告警消息，支持系统变量替换（使用 `${变量名}` 格式），默认：规则名称

**告警等级说明**：
- `INFO` - 信息类事件（探测、命中但未阻断），不需要立即处理
- `LOW` - 低风险（误报概率高），不需要立即处理
- `MEDIUM` - 可疑行为，需要关注
- `HIGH` - 高风险攻击，需要立即处理
- `CRITICAL` - 明确攻击 / 已造成影响，需要紧急处理

#### max_body_size

- **类型**: `number`
- **默认值**: `2048`
- **说明**: 请求体大小限制（字节），超过此大小的请求不进行内容检测。设置为 `0` 表示不限制。

#### exec_expr

- **类型**: `table`
- **必需**: 是
- **说明**: 基于系统变量的快速过滤表达式，用于快速决定是否进行内容检测。表达式格式见 [条件表达式.md](条件表达式.md)。如果未配置，该规则会被跳过。

**支持的变量**：
- `$method` - HTTP 方法
- `$http_request_uri` - 完整请求 URI
- `$http_content_type` - Content-Type 请求头
- `$remote_addr` - 客户端 IP
- 更多系统变量见 [变量.md](变量.md#系统变量列表)

**示例**：
```json
{
  "exec_expr": [
    "AND",
    ["$method", "==", "POST"],
    ["$http_content_type", "~~", "multipart/form-data"]
  ]
}
```

#### fetch_vars

- **类型**: `table`
- **必需**: 是（如果配置了 `success_expr`）
- **说明**: 自定义变量提取配置，用于从请求体、请求头等位置提取变量。详细配置见 [变量.md](变量.md#fetch_vars-详细格式配置)。

**支持的 source**：
- `request_body` - 从请求体中提取
- `var_ref` - 引用系统变量（可通过 `$http_xxx` 格式引用请求头）

**示例**：
```json
{
  "fetch_vars": {
    "filename": {
      "source": "request_body",
      "field": "filename=\"([^\"]+)\"",
      "parser": "regex"
    },
    "content_type": {
      "source": "var_ref",
      "field": "$http_content_type"
    }
  }
}
```

#### success_expr

- **类型**: `table`
- **必需**: 是
- **说明**: 基于自定义变量的表达式匹配，用于内容检测。表达式格式见 [条件表达式.md](条件表达式.md)。

**注意**：`success_expr` 中使用的变量必须通过 `fetch_vars` 提取，使用 `${变量名}` 格式引用。

**示例**：
```json
{
      "success_expr": [
        "OR",
        ["${filename}", "~~", ".php"],
        ["${filename}", "~~", ".jsp"],
        ["${filename}", "~~", ".asp"]
      ]
}
```

### rejected_msg

- **类型**: `string`
- **默认值**: 未配置
- **说明**: 阻断请求时的错误消息，支持系统变量替换（使用 `${变量名}` 格式）。如果未配置，将返回默认的 HTML 错误页面。

**注意**：兼容旧的 `reject_msg` 配置字段名。如果同时配置了 `rejected_msg` 和 `reject_msg`，优先使用 `rejected_msg`。

**示例**：
```json
{
  "rejected_msg": "危险请求，IP: ${remote_addr}"
}
```

## 完整配置示例

### 示例 1：文件上传检测

```json
{
  "excludes": [
    {
      "host": "example.com",
      "uris": ["^/api/public/upload"]
    }
  ],
  "rules": [
    {
      "name": "危险文件上传检测",
      "reject": true,
      "alert": {
        "event": "危险文件上传",
        "level": "HIGH",
        "message": "检测到危险文件上传：${filename}，来源IP：${remote_addr}"
      },
      "max_body_size": 10240,
      "exec_expr": [
        "AND",
        ["$method", "==", "POST"],
        ["$http_content_type", "~~", "multipart/form-data"]
      ],
      "fetch_vars": {
        "filename": {
          "source": "request_body",
          "field": "filename=\"([^\"]+)\"",
          "parser": "regex"
        }
      },
      "success_expr": [
        "OR",
        ["${filename}", "~~", ".php"],
        ["${filename}", "~~", ".jsp"],
        ["${filename}", "~~", ".asp"],
        ["${filename}", "~~", ".exe"],
        ["${filename}", "~~", ".sh"]
      ]
    }
  ],
  "rejected_msg": "不允许上传危险文件类型"
}
```

### 示例 2：JSON 请求体检测

```json
{
  "rules": [
    {
      "name": "SQL注入检测（JSON）",
      "reject": true,
      "alert": {
        "event": "SQL注入",
        "level": "HIGH",
        "message": "检测到SQL注入尝试：${sql_query}"
      },
      "max_body_size": 4096,
      "exec_expr": [
        "AND",
        ["$method", "==", "POST"],
        ["$http_content_type", "==", "application/json"]
      ],
      "fetch_vars": {
        "sql_query": {
          "source": "request_body",
          "field": "query",
          "parser": "json"
        }
      },
      "success_expr": [
        "OR",
        ["${sql_query}", "~~", "(?i)select\\s+.*\\s+from"],
        ["${sql_query}", "~~", "(?i)union\\s+.*\\s+select"],
        ["${sql_query}", "~~", "(?i)drop\\s+table"]
      ]
    }
  ]
}
```

### 示例 3：请求头检测

```json
{
  "rules": [
    {
      "name": "危险User-Agent检测",
      "reject": false,
      "alert": {
        "event": "可疑User-Agent",
        "level": "MEDIUM",
        "message": "检测到可疑User-Agent：${user_agent}"
      },
      "exec_expr": [
        ["$http_user_agent", "~=", ""]
      ],
      "fetch_vars": {
        "user_agent": {
          "source": "var_ref",
          "field": "$http_user_agent"
        }
      },
      "success_expr": [
        "OR",
        ["${user_agent}", "~~", "(?i)sqlmap"],
        ["${user_agent}", "~~", "(?i)nikto"],
        ["${user_agent}", "~~", "(?i)masscan"]
      ]
    }
  ]
}
```

## 日志记录

插件在 `log` 阶段记录告警日志，日志包含以下字段：

- `trace_id` - 请求追踪 ID
- `plugin_name` - 插件名称：`request_blocker`
- `action` - 动作：`block`（阻断）或 `pass`（仅记录）
- `event` - 告警事件名称
- `level` - 告警等级
- `message` - 告警消息（支持系统变量替换）
- `time` - 请求时间戳
- `ip` - 客户端 IP
- `app_id` - 应用 ID
- `app_name` - 应用名称
- `tenant_id` - 租户 ID
- `tenant_name` - 租户名称
- `url` - 完整请求 URL
- `request` - 请求信息（header、method、body）
  - `body` - 请求体（base64 编码，仅在 `max_body_size > 0` 时包含）

## 注意事项

1. **性能优化**：
   - 插件使用 LRU 缓存缓存预处理后的配置对象
   - 强烈建议配置 `exec_expr` 进行快速过滤，避免对大量请求进行内容检测
   - `max_body_size` 限制可以避免处理过大的请求体

2. **规则匹配顺序**：规则按配置顺序匹配，命中第一个规则后停止匹配。

3. **排除规则**：排除规则优先于检测规则，匹配排除规则的请求将跳过所有检测。

4. **变量提取**：
   - `fetch_vars` 提取的变量是插件私有的，不会注册到系统变量中
   - `success_expr` 中必须使用 `${变量名}` 格式引用 `fetch_vars` 提取的变量
   - `success_expr` 可以同时使用系统变量和自定义变量

5. **请求体处理**：
   - 请求体仅在 `max_body_size > 0` 且请求体大小不超过限制时才会被读取
   - 请求体内容会以 base64 编码的形式记录在告警日志中

6. **变量替换**：`alert.message` 和 `rejected_msg` 支持系统变量替换，使用 `${变量名}` 格式。

7. **与 uri_blocker 的区别**：
   - `uri_blocker` 基于系统变量检测 URI，不支持请求体检测
   - `request_blocker` 支持请求体和请求头检测，需要先提取自定义变量再进行匹配
