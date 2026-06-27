---
title: AI Bidding Multi Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# AI招投标多智能体系统

企业日常需要人工审阅大量招标文件，效率低、遗漏风险高。本项目实现上传招标PDF后，由 Router 总调度四个独立 Skill Agent，在本地自动完成投标研判、资质打分、风险审查和投标方案初稿生成，贴合赛事主题“让 Agent 真正进入企业工作流”。

本项目包含完整四层：

- 前端：`static/index.html`、`static/styles.css`、`static/app.js`
- 接口：`api.py`、`API.md`、`postman_collection.json`
- 后端业务：`router.py`、`skills/`、`utils.py`
- 服务端：`server.py`、`run.py`、`simple_server.py`

## 目录结构

```text
.
├── AGENTS.md
├── README.md
├── api.py
├── API.md
├── router.py
├── run.py
├── server.py
├── simple_server.py
├── utils.py
├── PROJECT_STRUCTURE.md
├── postman_collection.json
├── requirements.txt
├── requirements-server.txt
├── demo_data
│   ├── README.md
│   ├── create_demo_data.py
│   ├── mock_tender.pdf
│   └── company_qualification.xlsx
├── outputs
├── static
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── skills
│   ├── skill1_pdf_parser
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   ├── test.py
│   │   └── demo_tender.txt
│   ├── skill2_qualification_matcher
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   ├── test.py
│   │   └── demo_qualification.csv
│   ├── skill3_risk_reviewer
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   ├── test.py
│   │   └── demo_risk_terms.txt
│   └── skill4_bid_writer
│       ├── SKILL.md
│       ├── main.py
│       └── test.py
└── tests
    └── test_router.py
```

## 文件功能说明

| 文件/目录 | 功能 |
| --- | --- |
| `AGENTS.md` | 项目全局智能体协作规则、依赖边界和输出规范。 |
| `router.py` | 多智能体总调度主程序，串联4个Skill并生成完整报告。 |
| `api.py` | FastAPI接口，支持上传PDF和企业资质文件。 |
| `run.py` | 一键启动脚本，优先启动FastAPI，失败时进入标准库降级演示服务。 |
| `simple_server.py` | 无uvicorn时的本地演示服务器，支持运行内置Demo。 |
| `utils.py` | 页码溯源、JSON/Markdown/PDF导出、文件名清洗等公共工具。 |
| `skills/skill1_pdf_parser` | PDF文档解析Agent，提取全文、表格、预算、截标时间、保证金、评分权重和废标条款。 |
| `skills/skill2_qualification_matcher` | 资质匹配打分Agent，读取Excel/CSV资质台账并输出0-100分、缺失材料和加分建议。 |
| `skills/skill3_risk_reviewer` | 投标风险审查Agent，识别高/中/低风险并附带依据、影响和应对方案。 |
| `skills/skill4_bid_writer` | 投标方案生成Agent，输出商务标、技术标大纲和Markdown投标初稿。 |
| `static` | 黑客松现场演示前端，支持拖拽上传、结果查看和导出下载。 |
| `demo_data` | 模拟招标文件和企业资质库，现场可直接跑完整闭环。 |
| `outputs` | 系统自动生成的研判报告和导出文件目录。 |

## 安装依赖

依赖限定为：

```bash
pip install -r requirements.txt
```

`requirements.txt` 内只包含：`pandas`、`openpyxl`、`fastapi`、`pdfplumber`、`pytesseract`。

如果要启用完整后端上传服务，安装服务端依赖：

```bash
pip install -r requirements-server.txt
```

`requirements-server.txt` 额外包含：`uvicorn`、`python-multipart`。

如需浏览器上传接口，建议额外确保本地已有 `uvicorn`。如果没有，`run.py` 会自动切换到轻量演示服务。

## 一键启动

```bash
python server.py
```

打开：

```text
http://127.0.0.1:8000
```

Windows 也可以直接双击：

```text
start_demo.bat
```

注意：本地网站依赖启动窗口保持运行。不要关闭启动窗口；关闭后 `http://127.0.0.1:8000` 会立刻打不开。

页面支持两种方式：

1. 上传 `demo_data/mock_tender.pdf` 和 `demo_data/company_qualification.xlsx`。
2. 点击“运行内置Demo”，直接跑完整业务闭环。

## 命令行运行完整流程

```bash
python router.py
```

运行后会在 `outputs/时间戳_文件名/` 下生成：

- `完整投标研判报告.json`
- `资质匹配打分.xlsx`
- `风险审查PDF报告.pdf`
- `投标方案Markdown初稿.md`

## 单元测试

不依赖 pytest 时，可直接运行：

```bash
python tests/test_router.py
python skills/skill1_pdf_parser/test.py
python skills/skill2_qualification_matcher/test.py
python skills/skill3_risk_reviewer/test.py
python skills/skill4_bid_writer/test.py
```

## 赛事答辩讲解文案

### 1. 痛点

企业投标前通常要人工审阅几十到数百页招标文件，逐条核对资质、废标条款、评分细则和技术响应要求。人工流程慢、容易漏项，而且审阅结果很难直接转化成投标材料。

### 2. 方案

本系统把投标研判拆成四个可扩展 Agent：

- PDF文档解析Agent负责把招标文件变成可追溯结构化数据。
- 资质匹配打分Agent负责判断企业是否满足硬性门槛。
- 投标风险审查Agent负责识别废标、成本和合同风险。
- 投标方案生成Agent负责把研判结果转成商务标、技术标初稿。

Router 作为总调度，把上传文件自动分发给四个Skill，并汇总成可导出的完整投标辅助材料。

### 3. 亮点

- 纯本地部署，不依赖云端服务，适合企业内网和保密场景。
- Skill完全解耦，能单独调试、单独升级。
- 每条关键信息绑定页码和原文片段，避免无依据输出。
- 一次上传直接输出三类材料：资质打分Excel、风险审查PDF、投标方案Markdown。

### 4. 现场演示路径

1. 启动 `python run.py`。
2. 打开前端页面。
3. 上传模拟招标PDF和企业资质Excel。
4. 展示四个Agent自动流转结果。
5. 下载三类导出文件，说明系统已经进入企业真实工作流。

### 5. 后续扩展

- 接入企业历史投标知识库和合同库。
- 增强OCR扫描件识别链路。
- 引入大模型进行条款语义理解和投标初稿润色。
- 增加企业微信/钉钉审批流，实现投标风险闭环。
# Docker Deployment

Run the full FastAPI + React stack:

```bash
docker compose up --build
```

Default URLs:

```text
Frontend: http://127.0.0.1:5173
Backend:  http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs
Health:   http://127.0.0.1:8000/health
```

Optional environment setup:

```bash
cp .env.example .env
```

Docker volumes:

```text
./database -> /app/database
./uploads  -> /app/uploads
./outputs  -> /app/outputs
```

The frontend nginx container proxies `/api` and `/health` to the backend service.

## Hugging Face Spaces 部署

本项目支持 Hugging Face Docker Space 单容器部署。根目录 `Dockerfile` 会完成：

- 构建 Vite 前端：`npm install && npm run build`
- 安装 FastAPI 后端依赖
- 将 `frontend/dist` 复制到后端容器 `/app/static`
- 由 FastAPI 同时提供 API 和前端静态页面
- 监听 Hugging Face Spaces 标准端口 `7860`

部署到 Hugging Face Spaces 时选择：

```text
SDK: Docker
Port: 7860
```

前端默认使用同域相对 API 请求，例如：

```text
/api/v1/auth/login
/api/v1/projects/{project_id}/files
/api/v1/projects/{project_id}/analysis/start
```

因此在 Hugging Face 单容器部署时不需要配置独立后端网址，也不要把 `VITE_API_BASE_URL` 设置为本地地址。

建议在 Hugging Face Spaces 的 Secrets 中配置：

```text
JWT_SECRET=your-random-secret
```

可选配置：

```text
DATABASE_URL=sqlite:////tmp/ai-bidding/app.db
UPLOAD_DIR=/tmp/uploads
OUTPUT_DIR=/tmp/outputs
MAX_UPLOAD_SIZE_MB=50
```
