# WEB隐身盾暴露面收敛配置文档

## 概述

本文档介绍 WEB隐身盾网关针对暴露面收敛场景的插件编写方案。通过适配应用的认证机制，实现应用零改造的暴露面收敛。

## 适用场景

**✅ 适合使用零改造引擎规则的场景：**

- 企业内部应用（OA/ERP/财务/CRM等）需要暴露面收敛
- 希望在不修改应用代码的情况下，实现暴露面收敛
- 需要弱密码实时拦截和暴力破解防护
- 需要隐藏后端服务接口，降低被扫描和攻击风险
- 需要满足等保、数据安全法等合规要求

**❌ 不适合的场景：**

- 纯静态网站（无需认证）
- 需要深度定制认证流程且无法通过配置实现

**🚀 快速开始：** 如果你是第一次使用，建议先阅读 [5分钟编写应用插件.md](5分钟编写应用插件.md)

## 文档目录

| 文档 | 说明 |
|------|------|
| [FAQ.md](FAQ.md) | ⭐ **新手上路必读** WEB隐身盾常见问题 |
| **[5分钟编写应用插件.md](5分钟编写应用插件.md)** | ⭐ **新手上路必读**：最小化配置示例、分步配置指南、常见场景模板、快速验证方法 |
| **[快速开始.md](快速开始.md)** | ⭐ **新手上路必读**：快速开始文档  |
| **[应用插件文档.md](应用插件文档.md)** | ⭐ **新手上路必读**：应用插件编写文档 |
| [白名单.md](白名单.md) | 白名单配置文档 |
| [exposure_auth.md](exposure_auth.md) | 暴露面认证插件，基于 WISID 或应用自身 cookie/header 进行身份验证 |
| [exposure_login.md](exposure_login.md) | 登录接口插件，Hook 应用登录接口，判定登录成功/失败 |
| [exposure_session.md](exposure_session.md) | 用户会话处理模块 |
| [exposure_user.md](exposure_user.md) | 用户信息获取插件，通过子请求获取用户身份信息 |
| [uri_bypass.md](uri_bypass.md) | 正则白名单 URI 插件，基于正则表达式的白名单配置 |
| [uri_blocker.md](uri_blocker.md) | 请求头检测与拦截 |
| [request_blocker.md](request_blocker.md) | 请求体检测与拦截 |
| [passwd_bruteforce.md](passwd_bruteforce.md) | 登录口暴力破解检测与拦截 |
| [passwd_capture.md](passwd_capture.md) | 登录口密码捕获 |
| [passwd_restriction.md](passwd_restriction.md) | 登录口弱密码检测与拦截 |
| [sub-route.md](sub-route.md) | 子路由配置文档，基于 radixtree 的高效路由匹配 |
| [ctx-var.md](ctx-var.md) | 请求上下文变量文档，支持的 `$xxx` 变量说明 |
| [lua-resty-expr.md](lua-resty-expr.md) | 表达式语法文档，用于条件判定 |
| [path-syntax.md](path-syntax.md) | 路径提取语法文档，JSON/XML 路径语法说明 |
| [变量分类说明.md](变量分类说明.md) | 变量分类说明文档，涵盖三种变量，系统内部变量，过程内部变量，用户自定义变量 |
| [条件表达式.md](条件表达式.md) | 条件表达式 |
| [业务流程架构图.md](业务流程架构图.md) | 业务流程架构图 |
| [子路由.md](子路由.md) | 子路由配置文档 |
| [正则表达式性能优化指南.md](正则表达式性能优化指南.md) | 正则表达式性能优化指南，正则表达式性编写的注意事项 |
| [插件合规性审计清单.md](插件合规性审计清单.md) | 插件合规性审计清单，用于审计插件是否符合新引擎规范 |
| [plugin-config.schema.json](plugin-config.schema.json) | 插件配置 JSON Schema，用于结构校验与 IDE 支持 |
| [Cursor+HAR编写零改造插件规则实践手册.md](Cursor+HAR编写零改造插件规则实践手册.md) | Cursor+HAR 编写零改造插件规则实践手册 |

## 核心模块

针对暴露面收敛场景，除了防攻击的通用模块外，抽象出四个业务相关的核心模块：

| 模块名称 | 用途 |
|---------|------|
| `exposure_auth` | 暴露面收敛的鉴权模块，用户配置未得到WISID认证时候的处理方式 |
| `exposure_login` | Hook 应用的登录接口，判定登录请求的成功/失败，支持密码策略 |
| `exposure_user` | 判定请求是否已登录，同时获取用户身份信息（user_id、user_name） |
| `exposure_session` |  定义如何设置WISID会话

**详细说明见：** [5分钟编写应用插件.md](5分钟编写应用插件.md#核心概念2分钟理解)

## 代码插件配置优先级

```
代码插件内联配置 > 应用作用域配置 > 全局默认配置
```

即：**局部插件组配置 > 应用作用域配置 > 全局作用域配置**

### 代码插件数组元素格式

`plugins` 数组支持两种元素格式：

| 格式 | 说明 | 配置查找顺序 |
|------|------|-------------|
| `"plugin_name"` | 字符串（代码插件名称） | 应用 `plugin_confs` → 全局默认配置 |
| `{"name": "xxx", "conf": {...}}` | 对象（内联配置） | 直接使用 `conf` 中的配置 |

**详细说明见：** [5分钟编写应用插件.md](5分钟编写应用插件.md#核心概念2分钟理解)

### 示例说明

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
#### 插件配置头说明
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

  以上字段必须要有，plugin_for_app_name和plugin_for_app_version和plugin_description要给界面用户选择的。
  plugin_need_engine_version 需要多少版本之上的引擎


#### 上述配置中：
- `"redirect"` - 字符串格式，在 `plugin_confs` 中未定义，使用**全局默认配置**
- `"uri_bypass"` - 字符串格式，使用 `plugin_confs` 中定义的**应用作用域配置**
- `{"name": "exposure_auth", ...}` - 对象格式，直接使用**内联的 conf 配置**（优先级最高）
- `"app_logger"` - 字符串格式，在 `plugin_confs` 中未定义，使用**全局默认配置**

## 配置结构

### 完整配置示例

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

### 配置项说明

| 配置项 | 说明 |
|--------|------|
| 版本信息字段 | 若干版本信息字段，必填 |
| `user_configures` | 提供用户界面配置项目 ，选项 |
| `plugins` | 应用主插件组，直接定义插件列表，处理除特殊接口外的所有请求 |
| `plugin_group_id` | 引用已定义的插件组 ID，与 `plugins` **二选一**，`plugins` 优先级更高 |
| `sub_routes` | 子路由配置，用于特殊接口（如登录接口）使用不同的插件组 |
| `plugin_groups` | 应用作用域的插件组定义，可被子路由或 `plugin_group_id` 引用 |
| `plugin_confs` | 应用作用域的插件配置，插件组内只写插件名时从此处查找配置 |

**注意**：`plugins` 和 `plugin_group_id` 二选一配置：
- `plugins`：直接在应用配置中定义插件列表
- `plugin_group_id`：引用 `plugin_groups` 中定义的插件组，适合插件组复用场景
- 如果同时配置，`plugins` 优先级更高

### 用户界面配置
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
  **字段说明**：
  - `label`： label 展示给用户看的标签
  - `json_path`： json路径，界面会按照配置用户配置自定制的值，界面保存的时候会替换对应的json_path的对应的值
  - `type`: 字段类型，int,text,bool,json,select（单选）和mult_select（多选），并且增加预选值options. select和mult_select的时候还需要定义value_type
  - `value`：字段值，当type为select/mult_select的时候，value为数组，数组里的字段类型为value_type指定
  - `value_type`：只有在select/mult_select的时候才有效
  - `description`：展示给用户看的描述

### 子路由配置

子路由用于为特殊接口配置不同的插件组。使用 `resty.radixtree`（基数树）进行高效的路径匹配。

**注意**：由于主应用已经根据 Host 进行了匹配，子路由匹配时**不再进行 Host 匹配**，仅匹配 URI、HTTP 方法和自定义条件。

详细配置说明见 [sub-route.md](sub-route.md)。


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

**字段说明**：
- `uri` / `uris` - 匹配的 URI 路径（支持精确匹配、前缀匹配 `/*`、参数匹配 `/:id`）
- `methods` - 匹配的 HTTP 方法
- `vars` - 额外的匹配条件（可选），使用 [lua-resty-expr](lua-resty-expr.md) 语法

**vars 变量来源**：`vars` 中参与匹配的变量来源于 `ctx.var`，为平台内置变量（包括 WEB隐身盾 变量），常用变量如：
- `arg_xxx` - URL 查询参数
- `http_xxx` - 请求头（如 `http_user_agent`）
- `cookie_xxx` - Cookie 值
- `remote_addr` - 客户端 IP
- `uri`、`host`、`method` 等 WEB隐身盾 内置变量

详细变量列表见 [ctx-var.md](ctx-var.md)。

## 白名单配置

支持两种方式配置白名单 URL，跳过安全检测：

| 方式 | 插件/配置 | 性能 | 适用场景 |
|------|----------|------|---------|
| 子路由白名单 | `sub_routes` + `plugins: []` | **更高**（基数树匹配） | 需要 HTTP 方法或条件匹配 |
| 正则白名单 | `uri_bypass` | 一般（正则匹配） | 需要复杂正则匹配（如扩展名） |

**详细配置说明见：** [白名单.md](白名单.md)

## 适配流程

针对暴露面收敛场景，应用适配主要包括以下步骤：

1. **分析应用认证机制**：确定登录接口、认证凭据、登录成功标识
2. **分析用户信息获取接口**：找到可验证登录状态并获取用户信息的接口
3. **分析白名单接口**：梳理无需认证即可访问的接口
4. **配置核心代码插件**：`exposure_session`、`exposure_user`、`exposure_auth`、`exposure_login`
5. **配置白名单**：使用子路由或正则白名单
6. **测试验证**：验证登录、认证、白名单等功能

**详细分步配置指南见：** [5分钟编写应用插件.md](5分钟编写应用插件.md#分步配置指南)

## 参考链接

- [exposure_auth 插件配置](exposure_auth.md)
- [exposure_login 插件配置](exposure_login.md)
- [exposure_user 插件配置](exposure_user.md)
- [正则白名单 URI 配置](uri_bypass.md)
- [子路由配置](sub-route.md)
- [请求上下文变量](ctx-var.md)
- [lua-resty-expr 表达式语法](lua-resty-expr.md)
- [路径提取语法](path-syntax.md)
