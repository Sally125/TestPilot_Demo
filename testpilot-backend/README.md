# TestPilot Backend

TestPilot 后端服务，提供 AI 测试脚本生成、执行和管理功能。

## 快速开始

### 1. 配置 AI API

要使用 AI 能力（如测试用例分析、脚本生成等），需要配置 DeepSeek API：

编辑 `.env` 文件：

```env
# ===== DeepSeek API 配置 =====
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.kukuit.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

**获取 API Key**:
1. 访问 DeepSeek 官方平台注册账号
2. 创建 API Key
3. 替换 `DEEPSEEK_API_KEY` 的值

> **提示**：若暂未配置 API Key，可直接查看项目中的演示视频，快速了解系统功能与使用流程。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

服务启动后访问: `http://localhost:8001`

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

## 功能特性

- ✅ AI 测试用例分析与脚本生成
- ✅ Playwright 测试脚本执行
- ✅ 登录态管理与会话生成
- ✅ 项目管理与配置
- ✅ 测试报告生成

## 目录结构

```
testpilot-backend/
├── app/              # 应用代码
│   ├── main.py       # 入口文件
│   ├── routes.py     # API 路由
│   ├── services.py   # 核心服务
│   ├── crud.py       # 数据库操作
│   ├── models.py     # 数据模型
│   └── db_models.py  # 数据库表模型
├── data/             # 数据存储
├── generated/        # 生成的脚本
└── .env              # 环境配置
```

## 注意事项

- API Key 涉及费用，请合理控制使用
- 首次运行需要安装 Playwright 浏览器：`playwright install`
- 建议在 `.gitignore` 中排除 `.env` 文件，避免泄露 API Key