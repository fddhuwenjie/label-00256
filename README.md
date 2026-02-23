# 企业微信表格操作 API 服务

面向日常测试工作的 Python RESTful API 服务架构，支持企业微信在线表格的读写操作。

## How to Run

### 方式一：Docker 运行（推荐）

```bash
docker compose up --build -d
```

服务启动后访问：http://localhost:8000

API 文档：http://localhost:8000/docs

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
| backend | RESTful API 服务 | 8000 |

## 测试账号

| 用途 | Key | Value |
|------|-----|-------|
| API认证 | X-API-Key | test-api-key-256 |

## 题目内容

设计一个面向日常测试工作的Python RESTful API服务架构，用于支持自动化测试调用。当前阶段需优先实现企业微信在线表格文件的操作功能，具体包括：
1. 接收JSON格式字符串并按指定格式写入Excel表格
2. 从Excel表格中读取指定单元格、行列范围或特定条件的内容并返回JSON格式数据

架构设计应具备可扩展性，以便未来平滑集成其他功能模块。

## 功能特性

- ✅ RESTful API 服务（FastAPI）
- ✅ 企业微信 API 认证与授权
- ✅ 在线表格读写操作
- ✅ 模块化架构设计
- ✅ 完善的错误处理和日志记录
- ✅ Swagger/OpenAPI 文档
- ✅ 身份验证和权限控制
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
│   │   └── health.py        # 健康检查
│   ├── services/            # 业务服务
│   │   ├── __init__.py
│   │   ├── wecom.py         # 企业微信服务
│   │   └── sheet_service.py # 表格服务
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
│       └── test_wecom.py
├── docs/                     # 文档
│   └── architecture.md      # 架构设计文档
├── docker-compose.yml
├── .gitignore
└── README.md
```

## API 接口

### 表格操作

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/sheets/write | 写入数据到表格 |
| GET | /api/v1/sheets/read | 读取表格数据 |
| GET | /api/v1/sheets/cell | 读取指定单元格 |
| GET | /api/v1/sheets/range | 读取指定范围 |
| POST | /api/v1/sheets/query | 条件查询 |

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
