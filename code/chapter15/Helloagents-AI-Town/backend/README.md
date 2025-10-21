# 赛博小镇 - FastAPI 后端

基于 HelloAgents 框架的 AI NPC 对话系统后端服务。

## 🎯 功能特性

### 核心功能
- ✅ **单个 NPC 对话**: 玩家与 NPC 实时对话，使用独立 Agent 处理
- ✅ **批量对话生成**: 定时批量生成所有 NPC 的自主对话，降低 API 成本 66%
- ✅ **状态管理**: 自动更新和缓存 NPC 状态
- ✅ **CORS 支持**: 支持 Godot HTML5 导出跨域访问

### NPC 角色
1. **张三** - Python 工程师 (工位区)
2. **李四** - 产品经理 (会议室)
3. **王五** - UI 设计师 (休息区)

## 📦 安装依赖

### 1. 安装 Python 依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量
创建`.env`文件或设置环境变量：

**注意**: 如果不配置 API 密钥，系统将使用预设对话模式运行。

## 🚀 启动服务

### 方法 1: 直接运行
```bash
python main.py
```

### 方法 2: 使用 uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：
- **API 文档**: http://localhost:8000/docs
- **根路径**: http://localhost:8000/

## 🧪 测试 API

运行测试脚本：
```bash
python test_api.py
```

测试内容包括：
1. ✅ 根路径访问
2. ✅ 健康检查
3. ✅ 获取 NPC 列表
4. ✅ 获取 NPC 状态
5. ✅ 与 NPC 对话
6. ✅ 获取 NPC 详情
7. ✅ 强制刷新状态

## 📡 API 接口

### 1. 获取 NPC 列表
```http
GET /npcs
```

响应示例：
```json
{
  "npcs": [
    {
      "name": "张三",
      "title": "Python工程师",
      "location": "工位区",
      "activity": "写代码",
      "available": true
    }
  ],
  "total": 3
}
```

### 2. 与 NPC 对话
```http
POST /chat
Content-Type: application/json

{
  "npc_name": "张三",
  "message": "你好,你在做什么?"
}
```

响应示例：
```json
{
  "npc_name": "张三",
  "npc_title": "Python工程师",
  "message": "你好!我正在优化一个多智能体系统的性能,挺有意思的。",
  "success": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. 获取 NPC 状态
```http
GET /npcs/status
```

响应示例：
```json
{
  "dialogues": {
    "张三": "终于把这个bug修复了,测试通过!",
    "李四": "下周的产品评审会需要准备一下资料。",
    "王五": "这个配色方案看起来不错,再调整一下细节。"
  },
  "last_update": "2024-01-15T10:30:00",
  "next_update_in": 25
}
```

### 4. 强制刷新状态
```http
POST /npcs/status/refresh
```

## 🏗️ 项目结构

```
backend/
├── main.py              # FastAPI主程序
├── config.py            # 配置文件
├── models.py            # 数据模型(Pydantic)
├── agents.py            # NPC Agent系统
├── batch_generator.py   # 批量对话生成器
├── state_manager.py     # NPC状态管理器
├── test_api.py          # API测试脚本
├── requirements.txt     # Python依赖
└── README.md           # 本文件
```

## 🎨 核心设计

### 批量对话生成
为了降低 API 成本和延迟，系统采用批量生成策略：

**传统方式**:
- 3 个 NPC × 每 30 秒 = 6 次 API 调用/分钟
- 每小时： 360 次调用

**批量方式**:
- 1 次批量调用/30 秒 = 2 次 API 调用/分钟
- 每小时： 120 次调用
- **成本降低 66%!**

### 工作流程
```
1. 定时器触发(30秒)
   ↓
2. 批量生成器构建提示词
   ↓
3. 一次LLM调用生成所有NPC对话
   ↓
4. 解析JSON响应
   ↓
5. 更新状态管理器缓存
   ↓
6. Godot客户端定时获取状态
```

## 🔧 配置说明

### config.py
```python
# NPC更新间隔(秒)
NPC_UPDATE_INTERVAL = 30

# LLM配置
OPENAI_MODEL = "gpt-4o-mini"  # 推荐使用mini版本降低成本
```

### 调整更新频率
修改`config.py`中的`NPC_UPDATE_INTERVAL`:
- 开发测试： 10 秒
- 正式运行： 30-60 秒
- 低成本模式： 120 秒

## 🐛 故障排查

### 问题 1: 启动失败
```
❌ LLM初始化失败
```
**解决**: 检查 OPENAI_API_KEY 环境变量是否设置

### 问题 2: 对话无响应
```
⚠️ 将使用预设对话模式
```
**解决**: 系统自动降级到预设对话，不影响基本功能

### 问题 3: CORS 错误
**解决**: 检查`config.py`中的`CORS_ORIGINS`配置

## 📝 开发建议

### 添加新 NPC
1. 在`agents.py`的`NPC_ROLES`中添加配置
2. 在`batch_generator.py`的`preset_dialogues`中添加预设对话
3. 重启服务

### 自定义对话风格
修改`agents.py`中的`create_system_prompt`函数

### 调整批量生成提示词
修改`batch_generator.py`中的`_build_batch_prompt`函数

## 📄 许可证

本项目遵循 HelloAgents 项目的开源协议。

