# 路径提取语法

本文档说明在 `fetch_vars` 和 `extract` 配置中，使用 `parser: "json"` 或 `parser: "xml"` 时的路径语法。

## JSON 路径语法

当 `parser` 设置为 `"json"` 时，支持两种路径格式：

### 1. 简单点号路径

使用点号 `.` 分隔的路径，直接按层级访问 JSON 对象的属性。

**格式**：`属性1.属性2.属性3`

**示例**：

```json
// 原始 JSON 数据
{
  "data": {
    "user": {
      "id": "12345",
      "name": "张三",
      "email": "zhangsan@example.com"
    },
    "token": "abc123"
  },
  "code": 200
}
```

| 路径表达式 | 提取结果 |
|-----------|---------|
| `data.user.id` | `"12345"` |
| `data.user.name` | `"张三"` |
| `data.token` | `"abc123"` |
| `code` | `200` |

**配置示例**：

```json
{
  "fetch_vars": {
    "user_id": {
      "source": "response_body",
      "field": "data.user.id",
      "parser": "json"
    },
    "user_name": {
      "source": "response_body",
      "field": "data.user.name",
      "parser": "json"
    }
  }
}
```

### 2. JSONPath 表达式

以 `$.` 开头的标准 JSONPath 表达式，支持更复杂的查询，包括数组访问、通配符、过滤器等。

**注意**：JSONPath 表达式返回的是**数组**，即使只匹配到一个元素，也会返回包含该元素的数组。

#### JSONPath 基本语法

| 符号 | 说明 | 示例 |
|------|------|------|
| `$` | 根对象 | `$` |
| `.` | 子元素访问 | `$.store.book` |
| `..` | 递归下降，搜索所有层级 | `$..author` |
| `*` | 通配符，匹配所有元素 | `$.store.*` |
| `[]` | 数组下标或属性访问 | `$.store.book[0]` |
| `[start:end]` | 数组切片 | `$.store.book[0:2]` |
| `[*]` | 数组所有元素 | `$.store.book[*]` |
| `[?()]` | 过滤器表达式 | `$.store.book[?(@.price<10)]` |
| `@` | 当前元素（在过滤器中使用） | `@.price` |

#### JSONPath 示例

```json
// 原始 JSON 数据
{
  "store": {
    "book": [
      {
        "category": "reference",
        "author": "Nigel Rees",
        "title": "Sayings of the Century",
        "price": 8.95
      },
      {
        "category": "fiction",
        "author": "Evelyn Waugh",
        "title": "Sword of Honour",
        "price": 12.99
      },
      {
        "category": "fiction",
        "author": "Herman Melville",
        "title": "Moby Dick",
        "price": 8.99
      }
    ],
    "bicycle": {
      "color": "red",
      "price": 19.95
    }
  }
}
```

| JSONPath 表达式 | 说明 | 返回结果 |
|----------------|------|---------|
| `$.store.book[*].author` | 所有书的作者 | `["Nigel Rees", "Evelyn Waugh", "Herman Melville"]` |
| `$..author` | 所有作者（递归查找） | `["Nigel Rees", "Evelyn Waugh", "Herman Melville"]` |
| `$.store.*` | store 下所有内容 | `[book数组, bicycle对象]` |
| `$..book[0]` | 第一本书 | `[{第一本书对象}]` |
| `$..book[-1]` | 最后一本书 | `[{最后一本书对象}]` |
| `$..book[0,1]` | 前两本书 | `[{第一本}, {第二本}]` |
| `$..book[0:2]` | 索引 0 到 1 的书（不含 2） | `[{第一本}, {第二本}]` |
| `$..book[?(@.price<10)]` | 价格小于 10 的书 | `[{第一本}, {第三本}]` |
| `$..book[?(@.category=="fiction")]` | 类别为 fiction 的书 | `[{第二本}, {第三本}]` |
| `$.store.bicycle.color` | 自行车颜色 | `["red"]` |

**配置示例**：

```json
{
  "fetch_vars": {
    "all_authors": {
      "source": "response_body",
      "field": "$..author",
      "parser": "json"
    },
    "first_book_title": {
      "source": "response_body",
      "field": "$.store.book[0].title",
      "parser": "json"
    },
    "cheap_books": {
      "source": "response_body",
      "field": "$.store.book[?(@.price<10)]",
      "parser": "json"
    }
  }
}
```

### JSONPath 过滤器表达式

过滤器使用 `[?()]` 语法，`@` 表示当前元素。

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `==` | 等于 | `[?(@.status=="active")]` |
| `!=` | 不等于 | `[?(@.status!="deleted")]` |
| `<` | 小于 | `[?(@.price<10)]` |
| `<=` | 小于等于 | `[?(@.price<=10)]` |
| `>` | 大于 | `[?(@.price>10)]` |
| `>=` | 大于等于 | `[?(@.price>=10)]` |
| `=~` | 正则匹配 | `[?(@.name=~/^test/)]` |

### 简单路径 vs JSONPath 选择建议

| 场景 | 推荐格式 | 原因 |
|------|---------|------|
| 提取单个固定字段 | 简单路径 | 更简洁，返回直接值 |
| 提取数组中所有元素的某个属性 | JSONPath | 支持 `[*]` 通配符 |
| 条件过滤 | JSONPath | 支持 `[?()]` 过滤器 |
| 递归查找 | JSONPath | 支持 `..` 递归下降 |
| 用于表达式判定 | 简单路径 | 返回直接值，可用于比较 |

**注意**：
- 简单路径返回**直接值**（字符串、数字、对象等）
- JSONPath 返回**数组**，需要配合 `[*]` 语法在 `user_id_var` 中提取第一个非空值

## XML 路径语法

> **TODO**: XML 解析功能待实现，计划使用 `xml2lua` 库（版本 1.5-2）进行 XML 解析。

当 `parser` 设置为 `"xml"` 时，将使用 `xml2lua` 库解析 XML 数据。具体路径语法文档待补充。

## 正则解析器

当 `parser` 设置为 `"regex"` 时，`field` 字段作为正则表达式使用，从原始文本中提取数据。

详细语法参见正则表达式文档。

**配置示例**：

```json
{
  "fetch_vars": {
    "session_id": {
      "source": "response_body",
      "field": "session_id[=:]\\s*([a-zA-Z0-9]+)",
      "parser": "regex"
    }
  }
}
```

## 使用建议

1. **优先使用简单路径**：对于结构清晰的 JSON，简单路径更易读易维护
2. **JSONPath 用于复杂查询**：需要数组遍历、条件过滤时使用 JSONPath
3. **注意返回类型**：JSONPath 返回数组，简单路径返回直接值
4. **正则作为兜底**：当 JSON 解析无法满足需求时，使用正则提取
5. **二次正则过滤**：可以配合 `regex` 字段对提取结果进行二次处理

