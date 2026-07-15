# TestPilot - AI 测试智能体

一个基于 AI 的智能测试助手，支持测试需求分析、用例设计、脚本生成、执行闭环等全流程自动化。

## 功能特性

- ✅ AI 测试需求分析与拆解
- ✅ 智能测试用例设计与生成
- ✅ Playwright 测试脚本自动生成
- ✅ 脚本稳定性检测与优化
- ✅ 测试执行与报告生成
- ✅ 登录态管理与会话生成
- ✅ 项目管理与配置

## 快速开始

### 1. 配置环境变量

项目包含 `.env.example` 模板文件，复制一份并重命名为 `.env`：

```bash
cd testpilot-backend
cp .env.example .env
```

编辑 `.env` 文件，配置 DeepSeek API Key（必填）：

```env
# ===== DeepSeek API 配置（必填）=====
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.kukuit.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

**获取 API Key**:
1. 访问 DeepSeek 官方平台注册账号
2. 创建 API Key
3. 替换 `DEEPSEEK_API_KEY` 的值

> **提示**：若暂未配置 API Key，可直接查看项目中的演示视频，快速了解系统功能与使用流程。

### 2. 安装后端依赖

```bash
cd testpilot-backend
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
cd testpilot-backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. 启动前端

使用浏览器打开 `AI测试智能体_TestPilot.html` 文件，或通过静态服务器访问：

```bash
python -m http.server 8080
```

然后访问：`http://localhost:8080/AI测试智能体_TestPilot.html`

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key（必填） | - |
| `DEEPSEEK_BASE_URL` | API 基础地址 | `https://api.kukuit.com` |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-v4-flash` |
| `APP_PORT` | 服务端口 | `8000` |
| `DEBUG` | 调试模式 | `true` |
| `BROWSER_TYPE` | Playwright 浏览器类型 | `chromium` |
| `BROWSER_TIMEOUT` | 浏览器操作超时（毫秒） | `60000` |

## 目录结构

```
TestPilot/
├── AI测试智能体_TestPilot.html    # 前端页面
├── testpilot-backend/             # 后端服务
│   ├── app/                       # 应用代码
│   │   ├── main.py                # 入口文件
│   │   ├── routes.py              # API 路由
│   │   ├── services.py            # 核心服务
│   │   ├── crud.py                # 数据库操作
│   │   ├── models.py              # 数据模型
│   │   └── db_models.py           # 数据库表模型
│   ├── data/                      # 数据存储
│   ├── generated/                 # 生成的脚本
│   └── .env                       # 环境配置
├── docs/                          # 文档
└── README.md                      # 项目说明
```

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **后端**: Python + FastAPI + Uvicorn
- **数据库**: SQLite + SQLAlchemy
- **AI**: DeepSeek API
- **测试**: Playwright

## 注意事项

- API Key 涉及费用，请合理控制使用
- 首次运行需要安装 Playwright 浏览器：`playwright install`
- `.env` 文件已在 `.gitignore` 中排除，避免泄露 API Key
- 前端通过 `API_BASE` 配置连接后端地址，默认为 `http://localhost:8001/api`