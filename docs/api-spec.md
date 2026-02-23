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
  "message": "操作成功",
  "data": { ... }
}
```

**错误响应：**
```json
{
  "detail": {
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

将数据写入企业微信在线表格。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_id | string | 是 | 表格文档 ID |
| sheet_id | string | 否 | 工作表 ID，默认第一个 |
| data | array | 是 | 单元格数据数组 |
| data[].row | int | 是 | 行号（从1开始） |
| data[].col | int | 是 | 列号（从1开始） |
| data[].value | any | 是 | 单元格值 |

#### 请求示例

```json
{
  "spreadsheet_id": "shtcnxxxxxx",
  "sheet_id": "Sheet1",
  "data": [
    {"row": 1, "col": 1, "value": "姓名"},
    {"row": 1, "col": 2, "value": "年龄"},
    {"row": 1, "col": 3, "value": "部门"},
    {"row": 2, "col": 1, "value": "张三"},
    {"row": 2, "col": 2, "value": 28},
    {"row": 2, "col": 3, "value": "技术部"}
  ]
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "成功写入 6 个单元格",
  "updated_cells": 6
}
```

---

### 3.2 读取表格数据

**GET** `/api/v1/sheets/read`

从企业微信在线表格读取全部数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_id | string | 是 | 表格文档 ID |
| sheet_id | string | 否 | 工作表 ID |

#### 请求示例

```
GET /api/v1/sheets/read?spreadsheet_id=shtcnxxxxxx
```

#### 响应示例

```json
{
  "success": true,
  "message": "读取成功",
  "data": [
    ["姓名", "年龄", "部门"],
    ["张三", 28, "技术部"],
    ["李四", 32, "产品部"]
  ],
  "rows": 3,
  "cols": 3
}
```

---

### 3.3 读取指定单元格

**GET** `/api/v1/sheets/cell`

读取单个单元格的值。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_id | string | 是 | 表格文档 ID |
| sheet_id | string | 否 | 工作表 ID |
| row | int | 是 | 行号（从1开始） |
| col | int | 是 | 列号（从1开始） |

#### 请求示例

```
GET /api/v1/sheets/cell?spreadsheet_id=shtcnxxxxxx&row=1&col=1
```

#### 响应示例

```json
{
  "success": true,
  "message": "读取成功",
  "value": "姓名",
  "row": 1,
  "col": 1
}
```

---

### 3.4 读取指定范围

**GET** `/api/v1/sheets/range`

读取指定行列范围的数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_id | string | 是 | 表格文档 ID |
| sheet_id | string | 否 | 工作表 ID |
| start_row | int | 是 | 起始行号（从1开始） |
| start_col | int | 是 | 起始列号（从1开始） |
| end_row | int | 是 | 结束行号 |
| end_col | int | 是 | 结束列号 |

#### 请求示例

```
GET /api/v1/sheets/range?spreadsheet_id=shtcnxxxxxx&start_row=1&start_col=1&end_row=3&end_col=3
```

#### 响应示例

```json
{
  "success": true,
  "message": "读取成功",
  "data": [
    ["姓名", "年龄", "部门"],
    ["张三", 28, "技术部"],
    ["李四", 32, "产品部"]
  ],
  "rows": 3,
  "cols": 3
}
```

---

### 3.5 条件查询

**POST** `/api/v1/sheets/query`

根据条件查询表格数据。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| spreadsheet_id | string | 是 | 表格文档 ID |
| sheet_id | string | 否 | 工作表 ID |
| conditions | array | 是 | 查询条件数组 |
| conditions[].col | int | 是 | 列号（从1开始） |
| conditions[].operator | string | 是 | 操作符 |
| conditions[].value | any | 是 | 比较值 |
| logic | string | 否 | 条件逻辑：and/or，默认 and |

**支持的操作符：**

| 操作符 | 描述 |
|--------|------|
| eq | 等于 |
| ne | 不等于 |
| gt | 大于 |
| ge | 大于等于 |
| lt | 小于 |
| le | 小于等于 |
| contains | 包含 |
| starts_with | 开头匹配 |
| ends_with | 结尾匹配 |

#### 请求示例

```json
{
  "spreadsheet_id": "shtcnxxxxxx",
  "conditions": [
    {"col": 3, "operator": "eq", "value": "技术部"},
    {"col": 2, "operator": "ge", "value": 25}
  ],
  "logic": "and"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "查询到 2 条记录",
  "data": [
    ["姓名", "年龄", "部门"],
    ["张三", 28, "技术部"],
    ["赵六", 30, "技术部"]
  ],
  "rows": 3,
  "cols": 3
}
```

---

### 3.6 本地 Excel 文件操作

#### 3.6.1 上传 xlsx 文件

**POST** `/api/v1/sheets/local/upload`

上传本地 xlsx 文件并解析。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file | file | 是 | xlsx 文件（multipart/form-data） |

#### 响应示例

```json
{
  "success": true,
  "message": "文件上传成功",
  "data": {
    "file_id": "local_abc123",
    "filename": "data.xlsx",
    "sheets": ["Sheet1", "Sheet2"],
    "row_count": 100,
    "column_count": 10
  }
}
```

#### 3.6.2 读取已上传的文件

**GET** `/api/v1/sheets/local/read/{file_id}`

读取已上传的 xlsx 文件内容。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file_id | string | 是 | 文件 ID（路径参数） |
| sheet_name | string | 否 | 工作表名称 |
| range | string | 否 | 读取范围，如 "A1:C10" |

#### 响应示例

```json
{
  "success": true,
  "message": "读取成功",
  "data": {
    "file_id": "local_abc123",
    "sheet_name": "Sheet1",
    "range": "A1:C10",
    "values": [["Name", "Age"], ["Alice", 25]],
    "row_count": 2,
    "column_count": 2
  }
}
```

#### 3.6.3 导出为 xlsx 文件

**POST** `/api/v1/sheets/local/export`

将数据导出为 xlsx 文件。

#### 请求参数

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| data | array | 是 | 二维数组数据 |
| filename | string | 否 | 文件名 |
| sheet_name | string | 否 | 工作表名称，默认 Sheet1 |

#### 请求示例

```json
{
  "data": [
    ["Name", "Age"],
    ["Alice", 25],
    ["Bob", 30]
  ],
  "filename": "export.xlsx",
  "sheet_name": "Data"
}
```

#### 响应示例

```json
{
  "success": true,
  "message": "导出成功",
  "data": {
    "file_id": "export_xyz789",
    "filename": "export.xlsx",
    "path": "/app/data/exports/export_xyz789.xlsx",
    "row_count": 3,
    "column_count": 2
  }
}
```

#### 3.6.4 下载导出的文件

**GET** `/api/v1/sheets/local/download/{file_id}`

下载导出的 xlsx 文件。

#### 响应

返回 xlsx 文件（application/vnd.openxmlformats-officedocument.spreadsheetml.sheet）

#### 3.6.5 删除文件

**DELETE** `/api/v1/sheets/local/{file_id}`

删除已上传或导出的文件。

#### 响应示例

```json
{
  "success": true,
  "message": "文件已删除"
}
```

#### 3.6.6 列出所有文件

**GET** `/api/v1/sheets/local/files`

列出所有已上传和导出的文件。

#### 响应示例

```json
{
  "success": true,
  "data": {
    "uploads": [
      {"file_id": "local_abc123", "filename": "local_abc123.xlsx", "size": 1024, "created_at": "2024-01-01T12:00:00"}
    ],
    "exports": [
      {"file_id": "export_xyz789", "filename": "export_xyz789.xlsx", "size": 512, "created_at": "2024-01-01T13:00:00"}
    ]
  }
}
```

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
            │  (API Key)    │      │ SheetService  │      │ (Token+数据)  │
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
│  权限检查       │──── 失败 ────► 返回 403
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
│  │  (内存)         │    │  (内存)         │            │
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
│  │  4. 写入操作后自动使相关缓存失效         │           │
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

### 5.2 阶段二：增强功能（已完成）

- [x] 本地 xlsx 文件操作
- [x] 表格数据缓存（TTL 5分钟）
- [x] 细粒度权限控制
- [x] API 文档完善
- [x] 集成测试

### 5.3 阶段三：扩展功能（规划中）

- [ ] Redis 缓存支持
- [ ] 批量操作优化
- [ ] WebSocket 实时通知
- [ ] 数据库集成
- [ ] TFS 系统对接

---

## 6. 权限控制设计

### 6.1 权限级别

| 权限 | 描述 |
|------|------|
| read | 读取表格数据 |
| write | 写入表格数据 |
| local | 本地 xlsx 文件操作 |
| admin | 管理员权限（包含所有权限） |

### 6.2 预置 API Key

| Key | 权限 | 速率限制 |
|-----|------|----------|
| test-api-key-256 | read, write, local, admin | 1000/min |
| readonly-key-256 | read | 100/min |
| readwrite-key-256 | read, write | 60/min |
| local-file-key-256 | read, write, local | 30/min |

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
│ 检查速率限制    │──── 超限 ────► 返回 429
└────────┬────────┘
         │ 通过
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
