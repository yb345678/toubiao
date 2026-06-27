# 项目分层结构说明

本项目按“前端 + 接口层 + 后端业务层 + 服务端启动层”组织。

## 1. 前端层

目录：

```text
static/
├── index.html
├── styles.css
└── app.js
```

职责：

- 提供招标PDF和企业资质库上传页面。
- 调用后端接口 `/api/analyze`、`/api/demo`。
- 展示四个Agent结果。
- 提供导出文件下载入口。

## 2. 接口层

文件：

```text
api.py
API.md
postman_collection.json
```

职责：

- `api.py` 定义 FastAPI 接口。
- `API.md` 提供接口说明。
- `postman_collection.json` 可导入 Postman 测试接口。

接口：

- `GET /health`
- `GET /api/demo`
- `POST /api/analyze`
- `GET /download`

## 3. 后端业务层

文件与目录：

```text
router.py
utils.py
skills/
├── skill1_pdf_parser/
├── skill2_qualification_matcher/
├── skill3_risk_reviewer/
└── skill4_bid_writer/
```

职责：

- `router.py` 负责多Agent总调度。
- `utils.py` 负责公共工具与导出能力。
- `skills` 内四个Agent完全解耦，可独立调试与扩展。

## 4. 服务端启动层

文件：

```text
server.py
run.py
simple_server.py
start_demo.bat
start_demo_8001.bat
start_demo_debug.bat
requirements-server.txt
```

职责：

- `server.py` 是推荐启动入口。
- `run.py` 优先启动 FastAPI + uvicorn。
- `simple_server.py` 是无 uvicorn 时的标准库降级服务端。
- `start_demo*.bat` 是 Windows 本地演示启动脚本。

## 5. Demo数据与测试

目录：

```text
demo_data/
tests/
```

职责：

- `demo_data` 存放模拟招标PDF与企业资质Excel。
- `tests` 验证完整业务闭环。
