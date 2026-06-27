# GitHub Pages部署说明

GitHub Pages 只能运行静态网页，不能运行 Python/FastAPI 后端。

因此本项目提供两种入口：

1. `index.html`
   - GitHub Pages 首页入口。
   - 纯静态演示模式。
   - 可以直接打开，不需要 Python 服务端。

2. `server.py`
   - 本地完整后端服务入口。
   - 支持真实上传、后端接口、多Agent调度和文件导出。
   - 需要在本地或服务器运行。

## GitHub Pages正确配置

在 GitHub 仓库中进入：

```text
Settings -> Pages
```

配置：

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

然后访问：

```text
https://你的用户名.github.io/仓库名/
```

如果仓库名是 `yb345678.github.io`，才访问：

```text
https://yb345678.github.io/
```

如果仓库名不是 `yb345678.github.io`，例如仓库名是 `ai-bidding-agent-system-fullstack`，则访问：

```text
https://yb345678.github.io/ai-bidding-agent-system-fullstack/
```

## 完整后端运行方式

GitHub Pages 无法运行后端。完整后端请本地运行：

```bash
pip install -r requirements-server.txt
python server.py
```

然后打开：

```text
http://127.0.0.1:8000
```
