# API 接口详细设计规范

## 1. 概述

本文档定义了企业微信表格操作 API 服务的接口规范，包括请求/响应格式、字段说明、错误码定义等。

## 2. 通用规范

### 2.1 基础信息

| 项目 | 说明 |
|------|------|
| 基础URL | `http://localhost:8010/api/v1` |
| 协议 | HTTP/HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

### 2.2 认证方式

所有 API 请求需要在 Header 中携带 API Key：

```
X-API-Key: your-api-key
```

### 2.3 通用响应格式

**成功响应：**
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### 2.4 错误码定义

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| AUTH_FAILED | 401 | 认证失败，API Key 无效 |
| PERMISSION_DENIED | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 请求参数验证失败 |
| WECOM_API_ERROR | 502 | 企业微信 API 调用失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| RATE_LIMITED | 429 | 请求频率超限 |

---

## 3. 接口详情

### 3.1 写入表格数据

**POST** `/api/v1/sheets/write`

将 JSON 数据写入企业微信在线表格。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_token | string | 是 | 表格文档 Token |
| sheet_id | string | 否 | 工作表 ID，默认第一个 |
| range | string | 是 | 写入范围，如 "A1:C10" |
| values | array | 是 | 二维数组，写入的数据 |
| value_input_option | string | 否 | 值输入选项：RAW/USER_ENTERED |

#### 请求示例

```json
{
  "spreadsheet_token": "shtcnxxxxxx",
  "sheet_id": "Sheet1",
  "range": "A1:C3",
  "values": [
    ["姓名", "年龄", "部门"],
    ["张三", 28, "技术部"],
    ["李四", 32, "产品部"]
  ],
  "value_input_option": "USER_ENTERED"
}
```

#### 响应示例

```json
{
  "success": true,
  "data": {
    "spreadsheet_token": "shtcnxxxxxx",
    "updated_range": "Sheet1!A1:C3",
    "updated_rows": 3,
    "updated_columns": 3,
    "updated_cells": 9
  },
  "message": "写入成功"
}
```

---

### 3.2 读取表格数据

**GET** `/api/v1/sheets/read`

从企业微信在线表格读取数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_token | string | 是 | 表格文档 Token |
| sheet_id | string | 否 | 工作表 ID |
| range | string | 是 | 读取范围，如 "A1:C10" |

#### 请求示例

```
GET /api/v1/sheets/read?spreadsheet_token=shtcnxxxxxx&range=A1:C10
```

#### 响应示例

```json
{
  "success": true,
  "data": {
    "range": "Sheet1!A1:C3",
    "values": [
      ["姓名", "年龄", "部门"],
      ["张三", 28, "技术部"],
      ["李四", 32, "产品部"]
    ],
    "row_count": 3,
    "column_count": 3
  },
  "message": "读取成功"
}
```

---

### 3.3 读取指定单元格

**GET** `/api/v1/sheets/cell`

读取单个单元格的值。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_token | string | 是 | 表格文档 Token |
| sheet_id | string | 否 | 工作表 ID |
| cell | string | 是 | 单元格地址，如 "A1" |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "cell": "A1",
    "value": "姓名",
    "type": "string"
  }
}
```

---

### 3.4 读取指定范围

**GET** `/api/v1/sheets/range`

读取指定行列范围的数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_token | string | 是 | 表格文档 Token |
| sheet_id | string | 否 | 工作表 ID |
| start_row | int | 是 | 起始行号（从1开始） |
| end_row | int | 是 | 结束行号 |
| start_col | int | 否 | 起始列号（从1开始） |
| end_col | int | 否 | 结束列号 |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "range": "A1:C3",
    "values": [...],
    "row_count": 3,
    "column_count": 3
  }
}
```

---

### 3.5 条件查询

**POST** `/api/v1/sheets/query`

根据条件查询表格数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_token | string | 是 | 表格文档 Token |
| sheet_id | string | 否 | 工作表 ID |
| conditions | array | 是 | 查询条件数组 |
| conditions[].column | string | 是 | 列名或列号 |
| conditions[].operator | string | 是 | 操作符：eq/ne/gt/lt/gte/lte/contains |
| conditions[].value | any | 是 | 比较值 |
| logic | string | 否 | 条件逻辑：AND/OR，默认 AND |

#### 请求示例

```json
{
  "spreadsheet_token": "shtcnxxxxxx",
  "conditions": [
    {"column": "部门", "operator": "eq", "value": "技术部"},
    {"column": "年龄", "operator": "gte", "value": 25}
  ],
  "logic": "AND"
}
```

#### 响应示例

```json
{
  "success": true,
  "data": {
    "total": 2,
    "rows": [
      {"姓名": "张三", "年龄": 28, "部门": "技术部"},
      {"姓名": "王五", "年龄": 30, "部门": "技术部"}
    ]
  }
}
```

---

### 3.6 本地 Excel 文件操作

#### 3.6.1 上传并读取本地 Excel

**POST** `/api/v1/sheets/local/upload`

上传本地 xlsx 文件并读取内容。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file | file | 是 | xlsx 文件（multipart/form-data） |
| sheet_name | string | 否 | 工作表名称 |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "file_id": "local_123456",
    "sheets": ["Sheet1", "Sheet2"],
    "row_count": 100,
    "column_count": 10
  }
}
```

#### 3.6.2 导出为本地 Excel

**POST** `/api/v1/sheets/local/export`

将数据导出为 xlsx 文件。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| data | array | 是 | 二维数组数据 |
| filename | string | 否 | 文件名 |
| sheet_name | string | 否 | 工作表名称 |

#### 响应

返回 xlsx 文件下载。

---

### 3.7 健康检查

**GET** `/health`

检查服务健康状态。

#### 响应示例

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mode": "mock",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 4. 数据流图

### 4.1 系统架构数据流

```
┌─────────────┐     HTTP/JSON      ┌─────────────────┐
│   客户端    │ ─────────────────► │   FastAPI 服务   │
│  (测试脚本) │ ◄───────────────── │   (Port 8010)   │
└─────────────┘                    └────────┬────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
            │   认证模块    │      │   表格服务    │      │   缓存模块    │
            │  (API Key)    │      │ SheetService  │      │ (Token缓存)   │
            └───────────────┘      └───────┬───────┘      └───────────────┘
                                           │
                          ┌────────────────┴────────────────┐
                          │                                 │
                          ▼                                 ▼
                  ┌───────────────┐                ┌───────────────┐
                  │  企业微信 API │                │  本地文件存储  │
                  │  (真实模式)   │                │  (Mock模式)   │
                  └───────────────┘                └───────────────┘
```

### 4.2 请求处理流程

```
请求到达
    │
    ▼
┌─────────────────┐
│  API Key 验证   │──── 失败 ────► 返回 401
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────┐
│  参数校验       │──── 失败 ────► 返回 422
└────────┬────────┘
         │ 成功
         ▼
┌─────────────────┐
│  检查运行模式   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│ Mock  │ │ 真实  │
│ 模式  │ │ 模式  │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│本地   │ │获取Token  │
│文件   │ │(带缓存)   │
└───┬───┘ └─────┬─────┘
    │           │
    │           ▼
    │     ┌───────────┐
    │     │调用企微API│
    │     └─────┬─────┘
    │           │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │  返回结果  │
    └───────────┘
```

### 4.3 缓存策略数据流

```
┌─────────────────────────────────────────────────────────┐
│                      缓存层                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  Token 缓存     │    │  表格数据缓存   │            │
│  │  (内存)         │    │  (可选Redis)    │            │
│  │                 │    │                 │            │
│  │  TTL: 7200s     │    │  TTL: 300s      │            │
│  │  (2小时)        │    │  (5分钟)        │            │
│  └────────┬────────┘    └────────┬────────┘            │
│           │                      │                      │
│           ▼                      ▼                      │
│  ┌─────────────────────────────────────────┐           │
│  │            缓存命中检查                  │           │
│  │  1. 检查是否存在                         │           │
│  │  2. 检查是否过期                         │           │
│  │  3. 命中则返回，未命中则请求源           │           │
│  └─────────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 初步实现计划

### 5.1 阶段一：核心功能（已完成）

- [x] FastAPI 服务框架搭建
- [x] API Key 认证机制
- [x] 企业微信 API 对接
- [x] 表格读写基础功能
- [x] Mock 模式支持
- [x] 单元测试

### 5.2 阶段二：增强功能（当前）

- [x] 本地 xlsx 文件操作
- [x] 表格数据缓存
- [x] 细粒度权限控制
- [x] API 文档完善

### 5.3 阶段三：扩展功能（规划中）

- [ ] Redis 缓存支持
- [ ] 批量操作优化
- [ ] WebSocket 实时通知
- [ ] 数据库集成
- [ ] TFS 系统对接

---

## 6. 权限控制设计

### 6.1 权限级别

| 级别 | 权限 | 描述 |
|------|------|------|
| read | 只读 | 仅能读取表格数据 |
| write | 读写 | 可读取和写入数据 |
| admin | 管理 | 完全权限，包括配置管理 |

### 6.2 API Key 权限配置

```yaml
api_keys:
  - key: "read-only-key-001"
    permissions: ["read"]
    rate_limit: 100/min
    
  - key: "read-write-key-001"
    permissions: ["read", "write"]
    rate_limit: 60/min
    
  - key: "admin-key-001"
    permissions: ["read", "write", "admin"]
    rate_limit: 30/min
```

### 6.3 权限检查流程

```
请求到达
    │
    ▼
┌─────────────────┐
│ 解析 API Key    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 查询 Key 权限   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检查接口所需权限│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
 权限足够   权限不足
    │         │
    ▼         ▼
  继续处理   返回 403
```
