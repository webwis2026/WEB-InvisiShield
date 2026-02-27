# URI Blocker 插件

URI 阻断插件，用于检测和阻断危险的 URI 请求。插件基于系统变量（如 `http_request_uri`、`http_uri`、`http_args` 等）进行表达式匹配，支持目录遍历、SQL 注入等常见攻击检测。

**重要说明**：在实际使用中，`uri_blocker` 的规则通常通过 OP 平台的 UI 界面统一配置并下发到网关，**一般不需要在应用的 JSON 配置（如 `gw_configures.plugin_confs`）中手动编写规则**。本文件中的配置结构和示例主要用于理解插件能力和便于调试。

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
    },
    {
      "host": "test.abc.com",
      "uris": ["^/public"]
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

#### match_expr

- **类型**: `table`
- **必需**: 是
- **说明**: 基于系统变量的表达式匹配，用于判定是否命中规则。表达式格式见 [条件表达式.md](条件表达式.md)。

**支持的变量**：
- `$method` - HTTP 方法
- `$http_request_uri` - 完整请求 URI（包含路径和参数）
- `$http_uri` - URI 路径（不包含参数）
- `$http_args` - URI 参数
- `$http_content_type` - Content-Type 请求头
- `$remote_addr` - 客户端 IP
- 更多系统变量见 [变量.md](变量.md#系统变量列表)

**示例**：
```json
{
  "rules": [
    {
      "name": "目录遍历",
      "reject": true,
      "alert": {
        "event": "目录遍历",
        "level": "HIGH",
        "message": "危险请求 ${http_request_uri}"
      },
      "match_expr": [
        "AND",
        ["$method", "==", "GET"],
        [
          "OR",
          ["$http_uri", "~~", "../"],
          ["$http_uri", "~~", "./../"]
        ]
      ]
    },
    {
      "name": "SQL注入",
      "reject": true,
      "alert": {
        "event": "SQL注入",
        "level": "HIGH",
        "message": "SQL注入尝试 ${http_request_uri}"
      },
      "match_expr": [
        "OR",
        ["$http_request_uri", "~~", "select\\s+from"],
        ["$http_request_uri", "~~", "table\\s+drop"]
      ]
    }
  ]
}
```

### rejected_msg

- **类型**: `string`
- **默认值**: 未配置
- **说明**: 阻断请求时的错误消息，支持系统变量替换（使用 `${变量名}` 格式）。如果未配置，将使用默认的 HTML 错误页面。

**注意**：兼容旧的 `reject_msg` 配置字段名。如果同时配置了 `rejected_msg` 和 `reject_msg`，优先使用 `rejected_msg`。

**示例**：
```json
{
  "rejected_msg": "危险请求，IP: ${remote_addr}"
}
```

## 完整配置示例

```json
{
  "excludes": [
    {
      "host": "example.com",
      "uris": ["^/api/public"]
    }
  ],
  "rules": [
    {
      "name": "目录遍历检测",
      "reject": true,
      "alert": {
        "event": "目录遍历",
        "level": "HIGH",
        "message": "检测到目录遍历尝试：${http_request_uri}，来源IP：${remote_addr}"
      },
      "match_expr": [
        "AND",
        ["$method", "==", "GET"],
        [
          "OR",
          ["$http_uri", "~~", "\\.\\./"],
          ["$http_uri", "~~", "\\.\\.\\\\"],
          ["$http_uri", "~~", "\\.\\.%2F"]
        ]
      ]
    },
    {
      "name": "SQL注入检测",
      "reject": true,
      "alert": {
        "event": "SQL注入",
        "level": "HIGH",
        "message": "检测到SQL注入尝试：${http_request_uri}"
      },
      "match_expr": [
        "OR",
        ["$http_request_uri", "~~", "(?i)select\\s+.*\\s+from"],
        ["$http_request_uri", "~~", "(?i)union\\s+.*\\s+select"],
        ["$http_request_uri", "~~", "(?i)drop\\s+table"],
        ["$http_request_uri", "~~", "(?i)delete\\s+from"]
      ]
    }
  ],
  "rejected_msg": "请求被拒绝：危险请求",
  "rejected_code": 403
}
```

## 日志记录

插件在 `log` 阶段记录告警日志，日志包含以下字段：

- `trace_id` - 请求追踪 ID
- `plugin_name` - 插件名称：`uri_blocker`
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
- `request` - 请求信息（header、method）

## 注意事项

1. **性能优化**：插件使用 LRU 缓存缓存预处理后的配置对象，提升性能。
2. **规则匹配顺序**：规则按配置顺序匹配，命中第一个规则后停止匹配。
3. **排除规则**：排除规则优先于检测规则，匹配排除规则的请求将跳过所有检测。
4. **表达式匹配**：`match_expr` 基于系统变量，不支持自定义变量提取。如需检测请求体内容，请使用 `request_blocker` 插件。
5. **变量替换**：`alert.message` 和 `rejected_msg` 支持系统变量替换，使用 `${变量名}` 格式。
