# WEB InvisiShield Exposure Surface Reduction Configuration

## Overview

This document describes the plugin configuration for WEB InvisiShield gateway in exposure surface reduction scenarios. By adapting to application authentication mechanisms, it enables exposure surface reduction without modifying application code.

## Applicable Scenarios

**✅ Scenarios suitable for zero-modification engine rules:**

- Enterprise internal applications (OA/ERP/Finance/CRM, etc.) requiring exposure surface reduction
- Exposure surface reduction without modifying application code
- Real-time weak password blocking and brute-force protection
- Hiding backend service interfaces to reduce scanning and attack risks
- Compliance with regulations such as Cybersecurity Law and Data Security Law

**❌ Scenarios not suitable:**

- Pure static websites (no authentication required)
- Deeply customized authentication flows that cannot be achieved through configuration

**🚀 Quick Start:** If this is your first time, we recommend reading [5分钟编写应用插件.md](5分钟编写应用插件.md) first.

## Document Index

| Document | Description |
|----------|-------------|
| [FAQ.md](FAQ.md) | ⭐ **Getting Started** – WEB InvisiShield FAQ |
| **[5分钟编写应用插件.md](5分钟编写应用插件.md)** | ⭐ **Getting Started** – Minimal config examples, step-by-step guide, common templates, quick validation |
| **[快速开始.md](快速开始.md)** | ⭐ **Getting Started** – Quick start guide |
| **[应用插件文档.md](应用插件文档.md)** | ⭐ **Getting Started** – Application plugin documentation |
| [白名单.md](白名单.md) | Whitelist configuration |
| [exposure_auth.md](exposure_auth.md) | Exposure authentication plugin – validates identity via WISID or application cookie/header |
| [exposure_login.md](exposure_login.md) | Login interface plugin – hooks application login, determines success/failure |
| [exposure_session.md](exposure_session.md) | User session handling |
| [exposure_user.md](exposure_user.md) | User info plugin – fetches user identity via sub-requests |
| [uri_bypass.md](uri_bypass.md) | Regex-based URI whitelist plugin |
| [uri_blocker.md](uri_blocker.md) | Request header inspection and blocking |
| [request_blocker.md](request_blocker.md) | Request body inspection and blocking |
| [passwd_bruteforce.md](passwd_bruteforce.md) | Login brute-force detection and blocking |
| [passwd_capture.md](passwd_capture.md) | Login password capture |
| [passwd_restriction.md](passwd_restriction.md) | Login weak password detection and blocking |
| [sub-route.md](sub-route.md) | Sub-route configuration – radixtree-based routing |
| [ctx-var.md](ctx-var.md) | Request context variables – `$xxx` reference |
| [lua-resty-expr.md](lua-resty-expr.md) | Expression syntax for condition evaluation |
| [path-syntax.md](path-syntax.md) | Path extraction syntax – JSON/XML path |
| [变量分类说明.md](变量分类说明.md) | Variable classification – system, process, and user-defined |
| [条件表达式.md](条件表达式.md) | Conditional expressions |
| [业务流程架构图.md](业务流程架构图.md) | Business flow architecture |
| [子路由.md](子路由.md) | Sub-route configuration |
| [正则表达式性能优化指南.md](正则表达式性能优化指南.md) | Regex performance tuning guide |
| [插件合规性审计清单.md](插件合规性审计清单.md) | Plugin compliance audit checklist |
| [plugin-config.schema.json](plugin-config.schema.json) | Plugin config JSON Schema – structure validation and IDE support |
| [Cursor+HAR编写零改造插件规则实践手册.md](Cursor+HAR编写零改造插件规则实践手册.md) | Cursor+HAR zero-modification plugin practice guide |

## Core Modules

For exposure surface reduction, four core modules are provided in addition to general attack protection:

| Module | Purpose |
|--------|---------|
| `exposure_auth` | Authentication module – configures behavior when WISID is not authenticated |
| `exposure_login` | Hooks application login interface – determines login success/failure, supports password policies |
| `exposure_user` | Determines if request is authenticated and fetches user identity (user_id, user_name) |
| `exposure_session` | Defines how WISID session is set |

**Details:** [5分钟编写应用插件.md](5分钟编写应用插件.md#核心概念2分钟理解)

## Plugin Configuration Priority

```
Inline plugin config > Application-scoped config > Global default config
```

That is: **Local plugin group config > Application-scoped config > Global config**

### Plugin Array Element Format

The `plugins` array supports two element formats:

| Format | Description | Config Lookup Order |
|--------|-------------|---------------------|
| `"plugin_name"` | String (plugin name) | Application `plugin_confs` → Global default |
| `{"name": "xxx", "conf": {...}}` | Object (inline config) | Uses `conf` directly |

**Details:** [5分钟编写应用插件.md](5分钟编写应用插件.md#核心概念2分钟理解)

### Example

```json
{
  "user_configures": [
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_code",
                    "type_comment": "int,text,bool,json,select（单选）和mult_select（多选），并且增加预选值options. select和mult_select的时候还需要定义value_type",
                    "type": "int",
                    "value": 403,
                    "description": "没有认证的流量处理方式 response_code"
                },
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "text",
                    "value": "禁止访问",
                    "description": "没有认证的流量处理方式 response_msg"
                },
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "enum",
                    "value_type": "text",
                    "value": ["禁止访问","xxx"],
                    "description": "没有认证的流量处理方式 response_msg"
                }
  ],
  "gw_configures" :{
      "plugin_name": "gitlab插件",
      "plugin_for_app_name": "gitlab",
      "plugin_for_app_version": "V1",
      "plugin_version": "1.0.0",
      "plugin_need_engine_version": "1.0",
      "plugin_author": "TigerSec",
      "plugin_description": "gitlab插件",
      "plugin_last_updated": "2025-12-18",



      "plugins": [
        "redirect",
        "uri_bypass",
        {
          "name": "exposure_auth",
          "conf": {
            "reject_unauthed": true,
            "response_code": 403
          }
        },
        "app_logger"
      ],
      "plugin_confs": {
        "uri_bypass": {
          "filters": ["^/health$"]
        }
      }
    }
}
```
#### Plugin Header Fields

```json
  "plugin_name": "gitlab插件",
  "plugin_for_app_name": "gitlab",
  "plugin_for_app_version": "V1",
  "plugin_version": "1.0.0",
  "plugin_need_engine_version": "1.0",
  "plugin_author": "TigerSec",
  "plugin_description": "gitlab插件",
  "plugin_last_updated": "2025-12-18",
```

All of the above fields are required. `plugin_for_app_name`, `plugin_for_app_version`, and `plugin_description` are used for UI selection. `plugin_need_engine_version` specifies the minimum engine version.

#### In the above config:

- `"redirect"` – String format, not defined in `plugin_confs`, uses **global default config**
- `"uri_bypass"` – String format, uses **application-scoped config** from `plugin_confs`
- `{"name": "exposure_auth", ...}` – Object format, uses **inline conf** (highest priority)
- `"app_logger"` – String format, not defined in `plugin_confs`, uses **global default config**

## Configuration Structure

### Full Configuration Example

```json
{
"user_configures": [
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_code",
                    "type_comment": "int,text,bool,json,select（单选）和mult_select（多选），并且增加预选值options. select和mult_select的时候还需要定义value_type",
                    "type": "int",
                    "value": 403,
                    "description": "没有认证的流量处理方式 response_code"
                },
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "text",
                    "value": "禁止访问",
                    "description": "没有认证的流量处理方式 response_msg"
                },
                {
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "enum",
                    "value_type": "text",
                    "value": ["禁止访问","xxx"],
                    "description": "没有认证的流量处理方式 response_msg"
                }
  ],
  "gw_configures":{
    "plugin_name": "gitlab插件",
    "plugin_for_app_name": "gitlab",
    "plugin_for_app_version": "V1",
    "plugin_version": "1.0.0",
    "plugin_need_engine_version": "1.0",
    "plugin_author": "TigerSec",
    "plugin_description": "gitlab插件",
    "plugin_last_updated": "2025-12-18",


    "plugins": [
      "redirect",
      "client_ip",
      "uri_bypass",
      "anony_attack_blocker",
      {
        "name": "exposure_auth",
        "conf": {
          "reject_unauthed": true,
          "response_code": 403,
          "response_msg": "禁止访问"
        }
      },
      "app_logger"
    ],
    "plugin_group_id": "default_group_id(引用已定义的插件组（与 plugins 二选一）)"
    "sub_routes": [
      {
        "name": "登录接口",
        "plugin_group_id": "login_gid",
        "routes": [
          {
            "uri": "/api/login",
            "methods": ["POST"]
          }
        ]
      },
      {
        "name": "移动端登录接口",
        "plugin_group_id": "mobile_login_gid",
        "routes": [
          {
            "uri": "/api/login",
            "methods": ["POST"],
            "vars": [
              ["$arg_type", "==", "mobile"]
            ]
          }
        ]
      },
      {
        "name": "白名单接口",
        "plugins": [],
        "routes": [
          {
            "uri": "/api/public_info",
            "methods": ["GET", "POST"]
          },
          {
            "uri": "/health",
            "methods": ["GET"]
          }
        ]
      }
    ],

    "plugin_groups": {
      "login_gid": [
        "redirect",
        "passwd_restriction",
        {
          "name": "exposure_login",
          "conf": {
            "fetch_vars": {
              "user_id": {
                "source": "response_body",
                "field": "data.user.id",
                "parser": "json"
              }
            },
            "user_id_var": "user_id",
            "success_expr": ["AND",
              ["${upstream_status}", "==", 200],
              ["${user_id}", "!=", ""]
            ],
            "log_request": true
          }
        },
        "gzip"
      ],
      "mobile_login_gid": [
        "redirect",
        "passwd_restriction",
        {
          "name": "exposure_login",
          "conf": {
            "fetch_vars": {
              "user_id": {
                "source": "response_body",
                "field": "data.uid",
                "parser": "json"
              }
            },
            "success_expr": ["${upstream_status}", "==", 200],
            "user_id_var": "${user_id}"

          }
        },
        "gzip"
      ]
    },

    "plugin_confs": {
      "anony_attack_blocker": {
        "allow_request": false,
        "policy": "local"
      },
      "passwd_bruteforce": {
        "allow_degradation": false,
        "rejected_msg": "{\"code\":10206,\"msg\":\"非法攻击\",\"status\":false}"
      },
      "passwd_restriction": {
        "rejected_code": 200,
        "rejected_msg": "弱密码禁止登录",
        "block_request": false
      },
      "uri_bypass": {
        "filters": [
          "^/public/.*",
          "^/static/.*"
        ]
      },
      "exposure_user": {
        "key_name":"xxxxx",
        "sub_requests": [
          {
            "name": "get_user",
            "desc": "获取用户",
            "uri": "/api/userinfo",
            "method": "GET",
            "headers": {
              "Cookie": "$http_cookie"
            },
            "fetch_vars": {
              "user_id": {
                "source": "response_body",
                "field": "data.uid",
                "parser": "json"
              }
            },
            "success_expr": ["${upstream_status}", "==", 200],
          }
        ],
        "user_id_var": "${get_user.user_id}",
        "user_name_var": "${get_user.user_name}"
      }
    }
  }
}
```

### Configuration Items

| Item | Description |
|------|-------------|
| Version fields | Several version fields, required |
| `user_configures` | UI configuration items, optional |
| `plugins` | Main plugin group – defines plugin list for all requests except special routes |
| `plugin_group_id` | References a plugin group ID; **mutually exclusive** with `plugins`; `plugins` takes precedence |
| `sub_routes` | Sub-route config – different plugin groups for special routes (e.g., login) |
| `plugin_groups` | Application-scoped plugin groups – referenced by sub routes or `plugin_group_id` |
| `plugin_confs` | Application-scoped plugin config – used when plugin name only is specified |

**Note:** `plugins` and `plugin_group_id` are mutually exclusive:

- `plugins`: Define plugin list directly in application config
- `plugin_group_id`: Reference plugin group by ID; useful for reuse
- If both are set, `plugins` takes precedence

### User Interface Configuration

```json
 "user_configures": [
                {
                    "label":"未认证请求",
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_code",
                    "type_comment": "int,text,bool,json,select（单选）和mult_select（多选），并且增加预选值options. select和mult_select的时候还需要定义value_type",
                    "type": "int",
                    "value": 403,
                    "description": "没有认证的流量处理方式 response_code"
                },
                {
                    "label":"未认证请求返回信息",
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "text",
                    "value": "禁止访问",
                    "description": "没有认证的流量处理方式 response_msg"
                },
                {
                    "label":"未认证请求返回信息",
                    "json_path": "gw_configures.plugins.exposure_auth.conf.response_msg",

                    "type": "enum",
                    "value_type": "text",
                    "value": ["禁止访问","xxx"],
                    "description": "没有认证的流量处理方式 response_msg"
                }
  ]
  ```

**Field descriptions:**

- `label`: Label shown to users
- `json_path`: JSON path – UI saves the value at this path when configured
- `type`: Field type – int, text, bool, json, select (single), mult_select (mult). For select/mult_select, `value_type` is required
- `value`: Field value; for select/mult_select, `value` is an array; element type is `value_type`
- `value_type`: Only used for select/mult_select
- `description`: Description shown to users

### Sub-Route Configuration

Sub-routes use different plugin groups for special routes. Matching uses `resty.radixtree` for efficient path matching.

**Note:** Host matching is already done by the main application; sub-routes match **only** URI, HTTP method, and custom conditions.

See [sub-route.md](sub-route.md) for details.

```json
{
  "name": "子路由名称",
  "plugin_group_id": "引用的插件组ID",
  "routes": [
    {
      "uri": "/api/login",
      "methods": ["POST"],
      "vars": [
        ["$arg_type", "==", "mobile"]
      ]
    }
  ]
}
```

**Field descriptions:**

- `uri` / `uris` – URI path(s) to match (exact, prefix `/*`, or parameter `/:id`)
- `methods` – HTTP methods to match
- `vars` – Additional match conditions (optional), using [lua-resty-expr](lua-resty-expr.md) syntax

**vars variable sources:** Variables in `vars` come from `ctx.var` (platform built-in variables, including WEB InvisiShield variables). Common examples:

- `arg_xxx` – URL query parameters
- `http_xxx` – Request headers (e.g., `http_user_agent`)
- `cookie_xxx` – Cookie values
- `remote_addr` – Client IP
- `uri`, `host`, `method` – WEB InvisiShield built-in variables

See [ctx-var.md](ctx-var.md) for the full variable list.

## Whitelist Configuration

Two methods allow bypassing security checks for certain URLs:

| Method | Plugin/Config | Performance | Use Case |
|--------|---------------|-------------|----------|
| Sub-route whitelist | `sub_routes` + `plugins: []` | **Higher** (radixtree) | When HTTP method or condition matching is needed |
| Regex whitelist | `uri_bypass` | Moderate (regex) | Complex regex patterns (e.g., file extensions) |

**Details:** [白名单.md](白名单.md)

## Adaptation Workflow

For exposure surface reduction, application adaptation typically follows these steps:

1. **Analyze authentication** – Identify login endpoints, credentials, and success indicators
2. **Analyze user info** – Find endpoints that verify login and return user identity
3. **Identify whitelist** – List routes that do not require authentication
4. **Configure core plugins** – `exposure_session`, `exposure_user`, `exposure_auth`, `exposure_login`
5. **Configure whitelist** – Use sub-routes or regex whitelist
6. **Test** – Verify login, authentication, and whitelist behavior

**Step-by-step guide:** [5分钟编写应用插件.md](5分钟编写应用插件.md#分步配置指南)

## References

- [exposure_auth plugin configuration](exposure_auth.md)
- [exposure_login plugin configuration](exposure_login.md)
- [exposure_user plugin configuration](exposure_user.md)
- [Regex whitelist URI configuration](uri_bypass.md)
- [Sub-route configuration](sub-route.md)
- [Request context variables](ctx-var.md)
- [lua-resty-expr expression syntax](lua-resty-expr.md)
- [Path extraction syntax](path-syntax.md)
