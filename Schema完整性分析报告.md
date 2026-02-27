# plugin-config.schema.json 完整性分析报告

基于 readme.md 及文档目录中所有相关文档的阅读，对 `plugin-config.schema.json` 的覆盖情况进行分析。

## 一、已覆盖项

### 1. 顶层结构
- `desc`：8 个必填字段（plugin_name、plugin_for_app_name、plugin_for_app_version、plugin_version、plugin_need_engine_version、plugin_author、plugin_description、plugin_last_updated）
- `user_configures`：UI 配置项映射
- `gw_configures`：网关配置

### 2. user_configures
- `json_path`、`type`、`description` 必填
- `type` 枚举：int、text、bool、json、select、mult_select、**enum**（已补充）
- `label` / `lable` 兼容
- select / mult_select 需 `value_type`、`options`

### 3. gw_configures
- `plugins`、`plugin_group_id`、`sub_routes`、`plugin_groups`、`plugin_confs`
- 主路由与子路由的 plugins / plugin_group_id 二选一

### 4. plugins 数组
- 支持字符串或内联对象
- 禁止 regex_whiteuri、exposure_session、exposure_user

### 5. sub_route
- `name`、`routes` 必填
- `plugins` 或 `plugin_group_id` 二选一

### 6. route_item
- `uri` 或 `uris` 二选一
- `methods` 枚举：GET、POST、PUT、DELETE、PATCH、HEAD、OPTIONS
- `vars` 支持 lua-resty-expr

### 7. plugin_confs

| 插件 | 覆盖情况 |
|------|----------|
| **uri_bypass** | filters（字符串数组）、rules（含 name、uris、ip_whitelist、ip_blacklist、ip_black_areas） |
| **exposure_session** | key_name（string/array）、cookie |
| **exposure_user** | key_name、sub_requests、user_id_var、user_name_var、cache_*、connection_keepalive_*；sub_request 含 exec_expr、query、connect/send/read_timeout |
| **uri_blocker** | excludes、rules、rejected_msg |
| **request_blocker** | excludes、rules、rejected_msg |

### 8. exposure_user sub_request
- name、uri、success_expr 必填
- method、query、headers、body、exec_expr、connect_timeout、send_timeout、read_timeout
- fetch_vars：source 枚举含 request_body、response_header、response_body、**var_ref**

---

## 二、本次补充项（2025-02 更新）

1. **user_configures.type**：增加 `enum`，兼容 readme 中旧配置
2. **exposure_user**：`user_id_var`、`user_name_var` 改为可选（文档标注为“推荐配置”）
3. **exposure_user.key_name**：支持 string 或 array（多候选 key）
4. **exposure_user sub_request**：增加 exec_expr、query、connect_timeout、send_timeout、read_timeout
5. **exposure_user**：增加 cache_succ_ttl、cache_fail_ttl、cache_size、connection_keepalive_timeout、connection_keepalive_pool
6. **fetch_vars.source**：增加 `var_ref`
7. **uri_bypass.rules**：细化结构（name、uris、ip_whitelist、ip_blacklist、ip_black_areas）
8. **plugin_confs**：增加 uri_blocker、request_blocker 结构定义

---

## 三、未在 Schema 中细化的项（有意保持宽松）

以下插件/配置在文档中有详细说明，但 Schema 采用 `additionalProperties` 或通用 `object` 处理，便于扩展和兼容：

| 插件/配置 | 说明 |
|-----------|------|
| **exposure_auth conf** | log_unauthed、reject_unauthed、response_code、response_headers、response_body 等，位于 plugins[].conf |
| **exposure_login conf** | fetch_vars、user_id_var、success_expr、save_session、log_method 等，位于子路由 plugins[].conf |
| **passwd_bruteforce** | count、time_window、block_ip、rejected_conf 等 |
| **passwd_capture** | get、set、uri_pattern、username_selector、password_selector 等 |
| **passwd_restriction** | blacklist、whitelist、enable_weakpass_dict、min_passwd_length 等 |
| **uri_blocker / request_blocker rules** | 规则内 name、reject、alert、exec_expr、fetch_vars、success_expr 等，通常由 OP 平台下发 |
| **ip_restriction、ua_restriction、anony_attack_blocker** | 通过 additionalProperties 允许 |

---

## 四、gw_configures 必填约束

readme 要求主路由配置 `plugins` 或 `plugin_group_id` 二选一。当前 Schema 未强制该约束，原因：
- 兼容历史配置
- 子路由可单独使用 plugin_group_id

如需严格校验，可在 `plugin-validate.py` 中增加业务规则检查。

---

## 五、验证建议

1. 使用 `plugin-validate.py` 对 examples 下所有配置进行校验
2. 新增插件文档时，同步更新 Schema 的 plugin_confs 定义
3. 对 exposure_auth、exposure_login 等常用插件，可考虑增加可选 conf 结构定义

---

*报告生成时间：2025-02*
