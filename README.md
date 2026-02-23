# 企业微信表格操作 API 服务

面向日常测试工作的 Python RESTful API 服务架构，支持企业微信在线表格的读写操作。

## How to Run

### 方式一：Docker 运行（推荐）

```bash
docker compose up --build -d
```

服务启动后访问：http://localhost:8010

API 文档：http://localhost:8010/docs

### 方式二：本地运行

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Services

| 服务 | 描述 | 端口 |
|------|------|------|
| backend | RESTful API 服务 | 8010 |

## Mock 模式说明

本项目支持 **Mock 模式**，当未配置企业微信凭证时自动启用：

- **启用条件**：环境变量 `WECOM_CORP_ID` 或 `WECOM_CORP_SECRET` 为空
- **Mock 行为**：
  - 写入操作：返回成功响应，数据存储到本地 `backend/data/mock_sheets.json`
  - 读取操作：从本地 Mock 文件读取数据
  - access_token：返回模拟 token `mock_access_token_xxx`
- **使用场景**：开发调试、单元测试、无企业微信账号时的功能验证
- **切换方式**：配置真实的企业微信凭证即可切换到真实模式

```bash
# Mock 模式（默认）
docker compose up --build -d

# 真实模式
WECOM_CORP_ID=xxx WECOM_CORP_SECRET=xxx docker compose up --build -d
```

## 测试账号

| 用途 | Key | 权限 |
|------|-----|------|
| 管理员 | test-api-key-256 | read, write, local, admin |
| 只读 | readonly-key-256 | read |
| 读写 | readwrite-key-256 | read, write |
| 本地文件 | local-file-key-256 | read, write, local |

### 权限说明

| 权限 | 描述 |
|------|------|
| read | 读取表格数据 |
| write | 写入表格数据 |
| local | 本地 xlsx 文件操作 |
| admin | 管理员权限（包含所有权限） |

## 题目内容

设计一个面向日常测试工作的Python RESTful API服务架构，用于支持自动化测试调用。当前阶段需优先实现企业微信在线表格文件的操作功能，具体包括：
1. 接收JSON格式字符串并按指定格式写入Excel表格
2. 从Excel表格中读取指定单元格、行列范围或特定条件的内容并返回JSON格式数据

架构设计应具备可扩展性，以便未来平滑集成其他功能模块。

## 功能特性

- ✅ RESTful API 服务（FastAPI）
- ✅ 企业微信 API 认证与授权
- ✅ 在线表格读写操作
- ✅ 本地 xlsx 文件读写操作
- ✅ 模块化架构设计
- ✅ 完善的错误处理和日志记录
- ✅ Swagger/OpenAPI 文档
- ✅ 细粒度权限控制（read/write/admin/local）
- ✅ 表格数据缓存（TTL 5分钟）
- ✅ Mock 模式支持
- ✅ 单元测试和集成测试

## 项目结构

```
.
├── backend/
│   ├── main.py              # 主程序入口
│   ├── config.py            # 配置管理
│   ├── requirements.txt     # Python依赖
│   ├── Dockerfile           # Docker构建
│   ├── api/                  # API路由
│   │   ├── __init__.py
│   │   ├── sheets.py        # 表格操作接口
│   │   ├── local_excel.py   # 本地Excel操作接口
│   │   └── health.py        # 健康检查
│   ├── services/            # 业务服务
│   │   ├── __init__.py
│   │   ├── wecom.py         # 企业微信服务
│   │   ├── sheet_service.py # 表格服务
│   │   └── local_excel.py   # 本地Excel服务
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic模型
│   ├── core/                # 核心模块
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证模块
│   │   ├── logger.py        # 日志模块
│   │   └── exceptions.py    # 异常处理
│   └── tests/               # 测试用例
│       ├── __init__.py
│       ├── test_sheets.py
│       ├── test_wecom.py
│       └── test_local_excel.py
├── docs/                     # 文档
│   ├── api-spec.md          # API接口详细规范
│   └── architecture.md      # 架构设计文档
├── docker-compose.yml
├── .gitignore
└── README.md
```

## API 接口

### 表格操作（企业微信在线表格）

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/sheets/write | 写入数据到表格 |
| GET | /api/v1/sheets/read | 读取表格数据 |
| GET | /api/v1/sheets/cell | 读取指定单元格 |
| GET | /api/v1/sheets/range | 读取指定范围 |
| POST | /api/v1/sheets/query | 条件查询 |

### 本地 Excel 文件操作

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/sheets/local/upload | 上传 xlsx 文件 |
| GET | /api/v1/sheets/local/read/{file_id} | 读取已上传的文件 |
| POST | /api/v1/sheets/local/export | 导出数据为 xlsx |
| GET | /api/v1/sheets/local/download/{file_id} | 下载导出的文件 |
| DELETE | /api/v1/sheets/local/{file_id} | 删除文件 |
| GET | /api/v1/sheets/local/files | 列出所有文件 |

### 系统接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /docs | API文档 |

## 配置说明

环境变量配置（可在 `.env` 文件中设置）：

```env
# 企业微信配置
WECOM_CORP_ID=your_corp_id
WECOM_CORP_SECRET=your_corp_secret
WECOM_AGENT_ID=your_agent_id

# API配置
API_KEY=test-api-key-256
DEBUG=false
```

## 扩展性设计

系统采用模块化架构，预留以下扩展接口：
- 数据库连接池及CRUD操作接口
- TFS项目管理系统集成
- 其他第三方服务集成
