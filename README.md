# rag-chat-widget

一个基于 React + FastAPI + LangChain 的 AI 聊天组件，支持 RAG 知识库检索，一键集成 AI 聊天功能。

## 特性

- 🚀 开箱即用的 React 组件
- 💬 流式输出（WebSocket）
- 📚 RAG 知识库检索支持
- 🎨 支持明暗主题
- 📱 响应式设计
- 🔧 高度可配置

## 安装

```bash
npm i @daddy_chentao/rag-chat-widget
# or
yarn add @daddy_chentao/rag-chat-widget
# or
pnpm add @daddy_chentao/rag-chat-widget
```

## 使用

```tsx
import { ChatWidget } from '@daddy_chentao/rag-chat-widget';
import type { ChatConfig } from '@daddy_chentao/rag-chat-widget';
import '@daddy_chentao/rag-chat-widget/style.css';
export default function App() {
  const config: ChatConfig = {
    position: 'bottom-right',
    theme: 'light',
    primaryColor: '#3b82f6',
    welcomeMessage: '你好！有什么可以帮助你的吗？',
    placeholder: '输入消息...',
    enableStreaming: true,
    enableHistory: true,
  };

  return <ChatWidget config={config} />;
}
```

## 配置项

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `position` | `'bottom-right' \| 'bottom-left' \| 'top-right' \| 'top-left'` | `'bottom-right'` | 挂件位置 |
| `theme` | `'light' \| 'dark' \| 'auto'` | `'light'` | 主题 |
| `primaryColor` | `string` | `'#3b82f6'` | 主题色 |
| `welcomeMessage` | `string` | - | 欢迎消息 |
| `placeholder` | `string` | `'输入消息...'` | 输入框占位符 |
| `enableStreaming` | `boolean` | `true` | 启用流式输出 |
| `enableHistory` | `boolean` | `true` | 启用历史记录 |
| `sessionId` | `string` | - | 会话 ID |
| `userId` | `string` | - | 用户 ID |

## 后端配置

需要配合后端 API 使用。后端项目基于 FastAPI + LangChain：

```bash
# 安装依赖
pip3 install -r requirements.txt
# 启动后端
cd backend
uvicorn app.main:app --reload
```

### 环境变量

| 变量名 | 说明 |
|--------|------|
| `LLM_API_KEY` | OpenAI API Key |
| `LLM_MODEL` | 模型名称（默认 deepseek-ai/DeepSeek-R1-0528-Qwen3-8B） |
| `LLM_BASE_URL` | API Base URL（可选） |
| `EMBEDDING_API_KEY` | Embedding API Key |
| `EMBEDDING_MODEL` | Embedding 模型 |

### 知识库

将文档放入 `backend/app/knowledge/` 目录（支持 `.txt`, `.md`），后端启动时自动加载。

## API 端点

- `POST /api/v1/chat` - 聊天接口
- `POST /api/v1/search` - 知识库搜索
- `WS /ws/chat` - WebSocket 流式聊天


## License

MIT
