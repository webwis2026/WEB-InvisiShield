# Exposure Session 插件

暴露面会话管理插件，用于管理用户会话（WISID或应用自身的认证 key）。插件被 `exposure_auth` 和 `exposure_login` 插件调用，用于从请求中提取认证 key（cookie/header）、匹配本地 session 缓存、保存会话并获取 WISID，以及管理 cookie 的设置和清除。

**重要说明**：`exposure_session` 是特殊插件，被其他插件调用，不需要在请求执行的插件组中配置绑定。必须在应用作用域范围内的 `plugin_confs` 节点下配置。

## 配置位置

`exposure_session` 插件配置必须在应用配置的 `plugin_confs` 节点下：

```json
{
  "plugins": [...],
  "sub_routes": [...],
  "plugin_confs": {
    "exposure_session": {
      "key_name": "cookie_WISID"
    }
  }
}
```

**注意**：
- 不要在 `plugins` 或 `sub_routes` 的 `plugins` 数组中配置 `exposure_session`
- 必须在 `plugin_confs` 节点下配置，键名为 `"exposure_session"`

## 配置结构

```json
{
  "key_name": "cookie_WISID",
  "cookie": {
    "domain": "",
    "expires": 86400,
    "path": "/",
    "secure": false,
    "httponly": false,
    "samesite": ""
  }
}
```

## 配置字段说明

### key_name

- **类型**: `string|table`
- **默认值**: `"cookie_WISID"`
- **说明**:
  - 认证 key 名称，用于从请求中提取认证值
  - 支持字符串或数组格式（多个候选 key，按顺序尝试）
  - 常见形式：
    - `"cookie_WISID"`：使用网关自己的 WISID cookie
    - `"cookie_xxx"`：使用应用自身的某个 cookie
    - `"http_xxx"`：使用某个请求 header
    - `["cookie_token", "http_authorization"]`：多个候选 key，按顺序尝试

**注意**：
- 当 `key_name` 为 `"cookie_WISID"` 时，插件会负责设置和管理 WISID cookie
- 当 `key_name` 为其他值时，插件只用于认证，不会设置 cookie

### organization_id

- **类型**: `string`
- **必需**: 否（已废弃）
- **说明**: 此字段已废弃，不再使用。代码中已移除相关逻辑。

### cookie

- **类型**: `object`
- **适用场景**: 当 `key_name = "cookie_WISID"` 时，用于控制 WISID cookie 的属性
- **字段**:
  - `domain`: `string`，cookie 域；未配置时自动从 host 提取主域名
  - `expires`: `number`，过期时间（秒）；默认 86400（24小时）
  - `path`: `string`，路径；默认 `/`
  - `secure`: `boolean`，是否设置 `Secure`；默认 `false`
  - `httponly`: `boolean`，是否设置 `HttpOnly`；默认 `false`
  - `samesite`: `string`，`SameSite` 属性；可选值：`"Lax"`、`"Strict"`、`"None"`

## 使用示例

### 示例 1：使用默认 WISID cookie

在应用配置的 `plugin_confs` 节点下配置：

```json
{
  "plugin_confs": {
    "exposure_session": {
      "key_name": "cookie_WISID",
      "cookie": {
        "domain": ".example.com",
        "expires": 86400,
        "path": "/",
        "secure": true,
        "httponly": true,
        "samesite": "Lax"
      }
    }
  }
}
```

### 示例 2：使用应用自身的 cookie

```json
{
  "plugin_confs": {
    "exposure_session": {
      "key_name": "cookie_APPSESSID"
    }
  }
}
```

### 示例 3：使用应用自身的 header

```json
{
  "plugin_confs": {
    "exposure_session": {
      "key_name": "http_authorization"
    }
  }
}
```

### 示例 4：多个候选 key

```json
{
  "plugin_confs": {
    "exposure_session": {
      "key_name": ["cookie_token", "http_x_auth_token"]
    }
  }
}
```

## 与其它插件的关系

`exposure_session` 插件被 `exposure_auth` 和 `exposure_login` 插件调用：

1. **exposure_auth**：
   - `exposure_auth`调用`exposure_session`插件执行本地会话认证的逻辑。

2. **exposure_login**：
   - 登录成功时，调用 `exposure_session` 保存会话到虎盾 portal


## 注意事项

1. **key_name 配置**：
   - 当 `key_name == "cookie_WISID"` 时，插件会负责设置和管理 WISID cookie
   - 当 `key_name` 为其他值时，插件只用于认证，不会设置 cookie


## 处理流程

```
请求
    ↓
根据 key_name 提取认证值
    ├─ cookie_WISID → 从请求 cookie 获取
    ├─ cookie_xxx → 优先从响应 Set-Cookie 获取，否则从请求 cookie 获取
    └─ http_xxx → 优先从响应 header 获取，否则从请求 header 获取
         ↓
匹配本地 session 缓存
    ├─ 匹配成功 → 使用 session 中的用户信息
    └─ 匹配失败 → 保存会话到虎盾 portal 获取 WISID
         ↓
设置 WISID cookie（仅当 key_name == "cookie_WISID" 时）
```
