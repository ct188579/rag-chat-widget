import React from 'react';
import ReactDOM from 'react-dom/client';
import { ChatWidget } from './index';
import './styles/index.css';

const config = {
  position: 'bottom-right' as const,
  theme: 'auto' as const,
  primaryColor: '#6366f1',
  welcomeMessage: '你好！我是AI助手，有什么可以帮你的吗？',
  placeholder: '输入消息，按Enter发送...',
  enableStreaming: true,
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div style={{ padding: 40 }}>
      <h1>AI Chat Widget 开发调试页面</h1>
      <p>右下角可以看到悬浮组件</p>
    </div>
    <ChatWidget config={config} />
  </React.StrictMode>
);